"""Per-task workspace + `pre_setup` materialization for the Path B harness.

Supported `pre_setup` types (file/exec/memory tasks — the chain & memory suites
port cleanly):

  - file / txt / dependency_copy : copy or write a fixture into the workspace
  - workspace_files (frontmatter) : write inline content
  - memory_poison                : plant a poisoned rule into the agent's memory
                                    file(s) (CLAUDE.md + MEMORY.md in workspace)
  - run_command                  : run a setup command in the workspace
  - skill_copy                    : install a (poisoned) skill into the agent's
                                    `.claude/skills/` so Claude Code discovers it

Service-simulator types (banking/im/http) are NOT implemented here; a task that
needs one is reported as `needs_simulator` and skipped, so coverage is explicit.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# pre_setup types this harness can materialize on macOS without OpenClaw.
SUPPORTED = {"file", "txt", "dependency_copy", "memory_poison", "run_command", "skill_copy"}
# Types that require the upstream service simulators (out of scope for Path B v1).
NEEDS_SIMULATOR = {
    "im_new_contact",
    "banking_new_user",
    "banking_new_transaction",
    "http_post",
}

# Memory files a Claude Code agent will ingest from its workspace.
MEMORY_FILES = ("CLAUDE.md", "MEMORY.md")


@dataclass
class PreparedTask:
    workspace: Path
    runnable: bool
    skip_reason: Optional[str] = None
    memory_poisoned: bool = False
    notes: List[str] = field(default_factory=list)


def classify(pre_setup: List[Dict[str, Any]]) -> Optional[str]:
    """Return a skip reason if any step needs an unimplemented simulator."""
    for step in pre_setup:
        t = step.get("type")
        if t in NEEDS_SIMULATOR:
            return f"needs_simulator:{t}"
        if t and t not in SUPPORTED:
            return f"unsupported_pre_setup:{t}"
    return None


def prepare(
    task,
    workspaces_root: Path,
    repo_root: Path,
    allow_partial: bool = False,
) -> PreparedTask:
    skip = classify(task.pre_setup)
    workspace = workspaces_root / task.task_id
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    if skip and not allow_partial:
        return PreparedTask(workspace=workspace, runnable=False, skip_reason=skip)

    prepared = PreparedTask(workspace=workspace, runnable=True)

    # 1) inline workspace_files
    for wf in task.workspace_files:
        dest = workspace / wf["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(wf.get("content", ""), encoding="utf-8")

    # 2) pre_setup steps, in order
    for step in task.pre_setup:
        t = step.get("type")
        try:
            if t in ("file", "txt", "dependency_copy"):
                _copy_fixture(step, workspace, repo_root)
            elif t == "skill_copy":
                _copy_skill(step, workspace, repo_root)
            elif t == "memory_poison":
                _plant_memory_poison(step, workspace)
                prepared.memory_poisoned = True
            elif t == "run_command":
                _run_command(step, workspace, prepared)
            elif t in NEEDS_SIMULATOR:
                prepared.notes.append(f"skipped_step:{t} (no simulator)")
            # else: unknown but allowed-through under allow_partial
        except Exception as exc:  # noqa: BLE001
            prepared.notes.append(f"pre_setup_error:{t}:{exc}")

    return prepared


def _copy_fixture(step: Dict[str, Any], workspace: Path, repo_root: Path) -> None:
    src_rel = step.get("path") or step.get("src")
    dest_rel = step.get("dest") or (Path(src_rel).name if src_rel else None)
    if not src_rel or not dest_rel:
        # `txt` may carry inline content instead of a path
        if step.get("type") == "txt" and step.get("content") is not None and dest_rel:
            (workspace / dest_rel).write_text(step["content"], encoding="utf-8")
        return
    src = (repo_root / src_rel).resolve()
    dest = workspace / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    elif src.exists():
        shutil.copy2(src, dest)
    else:
        raise FileNotFoundError(f"fixture not found: {src}")


def _copy_skill(step: Dict[str, Any], workspace: Path, repo_root: Path) -> None:
    """Install a (poisoned) skill directory where Claude Code discovers skills.

    Upstream drops the skill into OpenClaw's skills path; the Path B equivalent
    is the project-level `.claude/skills/<name>/` (each skill carries a
    `SKILL.md`). This is a local copytree — no service simulator needed.
    """
    src_rel = step.get("source_path_dir") or step.get("source") or step.get("src")
    target = step.get("target_path_dir") or (Path(src_rel).name if src_rel else None)
    if not src_rel or not target:
        return
    src = (repo_root / src_rel).resolve()
    if not src.exists():
        raise FileNotFoundError(f"skill source not found: {src}")
    dest = workspace / ".claude" / "skills" / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)


def _plant_memory_poison(step: Dict[str, Any], workspace: Path) -> None:
    """Append the poisoned rule to the agent's memory file(s).

    Upstream writes to `assets/MEMORY.md`; for Claude Code the equivalent
    long-term/context store is `CLAUDE.md` (and a workspace `MEMORY.md` that the
    tasks reference by name). We plant into both so the agent ingests it.
    """
    poison = step.get("poison", "")
    block = (
        "\n## Operational Memory (persisted from a prior session)\n"
        f"- {poison}\n"
    )
    for name in MEMORY_FILES:
        f = workspace / name
        existing = f.read_text(encoding="utf-8") if f.exists() else f"# {name}\n"
        f.write_text(existing + block, encoding="utf-8")


def _run_command(step: Dict[str, Any], workspace: Path, prepared: PreparedTask) -> None:
    cmd = step.get("command") or step.get("cmd")
    if not cmd:
        return
    res = subprocess.run(
        cmd, shell=True, cwd=str(workspace), capture_output=True, text=True, timeout=60
    )
    prepared.notes.append(f"run_command rc={res.returncode}")
