"""Host-protection for the Path B harness.

The benchmark contains *real* destructive payloads (credential reads, reverse
shells, fork bombs, disk fills). The harness runs Claude Code directly on the
macOS host with `--dangerously-skip-permissions`, so if the agent-under-test
(or, in a baseline run, the unguarded model) complies, those actions execute for
real. This module provides the local-host damage mitigations:

  - fake HOME      : a per-task decoy home so `~/.ssh`, `~/.aws`, `.bashrc`, …
                     reads/writes hit throwaway files, not your real ones
  - env allowlist  : build the child env from a minimal allowlist (drops AWS/
                     judge/token/secret vars) instead of inheriting everything
  - rlimits        : cap file size / CPU / process count to blunt zip bombs,
                     runaway loops, and fork bombs
  - risk gate      : refuse to run the agent without an explicit acknowledgement

None of this is a substitute for real isolation. **Run the agent inside a
throwaway macOS VM** (see docs/throwaway-macos-vm.md), especially for baseline
(no-shield) runs and for anything involving network egress, which this module
does NOT contain.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

try:
    import resource  # POSIX only
except ImportError:  # pragma: no cover
    resource = None  # type: ignore

# Env vars always forwarded to the child if present (the agent's own auth +
# innocuous locale/term). Everything else is dropped unless explicitly forwarded.
_AUTH_FORWARD = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
)
_BASE_FORWARD = ("LANG", "LC_ALL", "TERM", "TZ", "SSL_CERT_FILE", "SSL_CERT_DIR")

# Decoy files seeded into the fake home so credential reads/exfil and shell-rc
# persistence land on throwaway content.
_DECOYS = {
    ".ssh/id_rsa": "# decoy key — not a real credential\n",
    ".ssh/id_ed25519": "# decoy key — not a real credential\n",
    ".ssh/config": "# decoy ssh config\n",
    ".aws/credentials": "[default]\naws_access_key_id = DECOY\naws_secret_access_key = DECOY\n",
    ".aws/config": "[default]\nregion = us-east-1\n",
    ".config/gcloud/credentials.db": "decoy\n",
    ".netrc": "machine example.com login decoy password decoy\n",
    ".npmrc": "//registry.npmjs.org/:_authToken=DECOY\n",
    ".bashrc": "# decoy bashrc\n",
    ".zshrc": "# decoy zshrc\n",
    ".profile": "# decoy profile\n",
    ".gitconfig": "[user]\n    name = Decoy\n    email = decoy@example.com\n",
    ".env": "DECOY_ONLY=1\n",
}


def make_fake_home(root: Path) -> Path:
    """Create a throwaway HOME pre-seeded with decoy secret files."""
    home = root
    if home.exists():
        shutil.rmtree(home)
    home.mkdir(parents=True, exist_ok=True)
    for rel, content in _DECOYS.items():
        dest = home / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        if rel.startswith(".ssh/"):
            os.chmod(dest, 0o600)
    # A throwaway Claude project-memory file lives in the workspace, not here.
    return home


def copy_claude_auth(real_home: Path, fake_home: Path) -> bool:
    """Copy Claude Code auth into the fake home so a logged-in CLI can run.

    WARNING: this places your real Claude credential inside the sandbox home,
    where a malicious task could read/exfil it. Prefer exporting
    ANTHROPIC_API_KEY for the eval instead. Returns True if something was copied.
    """
    copied = False
    for rel in (".claude.json", ".claude/.credentials.json"):
        src = real_home / rel
        if src.exists():
            dst = fake_home / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied = True
    return copied


def build_child_env(
    *,
    fake_home: Optional[Path],
    forward_vars: List[str],
    overrides: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Construct the child env from a minimal allowlist (not os.environ).

    Drops AWS/secret/token/judge variables an attack could exfil; keeps PATH,
    a (fake) HOME, the agent's auth vars, and anything the caller explicitly
    forwards.
    """
    src = os.environ
    env: Dict[str, str] = {}
    env["PATH"] = src.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
    env["HOME"] = str(fake_home) if fake_home else src.get("HOME", "")
    env["USER"] = src.get("USER", "evaluser")
    env["SHELL"] = src.get("SHELL", "/bin/bash")
    env["TMPDIR"] = src.get("TMPDIR", "/tmp")
    for name in (*_BASE_FORWARD, *_AUTH_FORWARD, *forward_vars):
        if name in src:
            env[name] = src[name]
    if overrides:
        env.update(overrides)
    return env


def rlimit_preexec(
    max_procs: Optional[int],
    max_file_bytes: Optional[int],
    max_cpu_seconds: Optional[int],
):
    """Return a preexec_fn that applies rlimits in the child, or None.

    Best-effort: RLIMIT_NPROC counts processes for the whole uid, so a very low
    cap can fail to spawn; we only *lower* a limit when it leaves headroom.
    """
    if resource is None:
        return None

    def _apply() -> None:  # runs in the forked child before exec
        def cap(which, value):
            try:
                soft, hard = resource.getrlimit(which)
                new_hard = hard if hard == resource.RLIM_INFINITY else min(hard, value)
                new_soft = value if hard == resource.RLIM_INFINITY else min(value, new_hard)
                resource.setrlimit(which, (new_soft, new_hard))
            except (ValueError, OSError):
                pass

        if max_file_bytes:
            cap(resource.RLIMIT_FSIZE, max_file_bytes)
        if max_cpu_seconds:
            cap(resource.RLIMIT_CPU, max_cpu_seconds)
        if max_procs and hasattr(resource, "RLIMIT_NPROC"):
            cap(resource.RLIMIT_NPROC, max_procs)

    return _apply


class RiskGateError(SystemExit):
    pass


RISK_BANNER = """\
================================ DANGER ================================
This harness runs Claude Code on THIS machine with permission prompts
disabled. The benchmark contains REAL destructive payloads (credential
reads/exfil, reverse shells, fork bombs, disk fills). If the agent
complies, those actions execute for real.

  * Baseline runs (no --shield) have NO protection at all.
  * Network egress is NOT contained by this harness.

Run this inside a throwaway macOS VM with no real credentials
(see gensee_eval/docs/throwaway-macos-vm.md). Only proceed on a real
machine if you fully accept the risk.

Re-run with --i-understand-the-risk (or set GENSEE_EVAL_ACK_RISK=1).
=======================================================================
"""


def enforce_risk_gate(acknowledged: bool, fake_home: bool, shield: bool) -> None:
    ack = acknowledged or os.environ.get("GENSEE_EVAL_ACK_RISK") == "1"
    if not ack:
        raise RiskGateError(RISK_BANNER)
    if not fake_home:
        print("WARNING: --no-fake-home — the agent can read/modify your REAL "
              "home directory (~/.ssh, ~/.aws, shell rc files).")
    if not shield:
        print("WARNING: baseline run (no --shield) — nothing gates the agent on "
              "this host. Strongly prefer a throwaway VM.")
