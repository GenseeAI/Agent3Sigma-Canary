"""Gensee / agent-shield wiring for the Path B harness.

When `--shield` is on, we hand Claude Code a per-run settings file whose hooks
call the `gensee hook claude-code` bridge with a dedicated `GENSEE_HOME`, so the
deterministic PreToolUse policy is in the loop and the SQLite store/alerts are
isolated per run. After a task we can read the `alerts` table as ground-truth
telemetry (how many actions the shield actually blocked), independent of the
judge — this is the macOS stand-in for the upstream Tracee grounding.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

HOOK_EVENTS = ("UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop")


def make_settings(gensee_bin: Path, gensee_home: Path) -> Dict[str, Any]:
    # The hook command runs with the agent's cwd (the per-task workspace), so the
    # binary path and GENSEE_HOME must be absolute — otherwise the hook fails to
    # exec / writes its store under the workspace, and the shield silently sees
    # nothing.
    cmd = f"GENSEE_HOME={gensee_home.resolve()} {gensee_bin.resolve()} hook claude-code"
    hook = {"matcher": "*", "hooks": [{"type": "command", "command": cmd}]}
    return {"hooks": {event: [hook] for event in HOOK_EVENTS}}


def write_settings(path: Path, gensee_bin: Path, gensee_home: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(make_settings(gensee_bin, gensee_home), indent=2), encoding="utf-8")
    return path


def shield_env(base_env: Dict[str, str], gensee_home: Path, policy_file: Optional[Path]) -> Dict[str, str]:
    env = dict(base_env)
    env["GENSEE_HOME"] = str(gensee_home.resolve())
    if policy_file:
        env["GENSEE_POLICY_FILE"] = str(policy_file.resolve())
    return env


def read_alerts(gensee_home: Path) -> List[Dict[str, Any]]:
    """Return policy alerts from the per-run store, or [] if absent."""
    db = gensee_home / "gensee.db"
    if not db.exists():
        return []
    try:
        # NOT mode=ro: the store is WAL-journaled, and SQLite cannot open a WAL
        # database read-only (it needs write access to the -shm/-wal files), so
        # `?mode=ro` raised "unable to open database file" and the run reported
        # block=0. The run is finished by the time we read, so a normal
        # (read-write) connection is safe and sees the checkpointed alerts.
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            # ORDER BY rowid (insertion order) — robust to the timestamp column
            # name. The alerts table's column is `observed_at_ms`, NOT
            # `created_at`; ordering by created_at threw and the bare except
            # below silently returned [], so every shielded run reported
            # block=0 (the shield looked like it never fired).
            "SELECT rule_id, action, severity, path, message FROM alerts ORDER BY rowid"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except sqlite3.Error as exc:
        import sys
        print(f"    [shield] read_alerts failed for {db}: {exc}", file=sys.stderr)
        return []


def block_summary(alerts: List[Dict[str, Any]]) -> Dict[str, int]:
    out = {"block": 0, "ask": 0, "warn": 0, "allow": 0}
    for a in alerts:
        out[a.get("action", "allow")] = out.get(a.get("action", "allow"), 0) + 1
    return out
