"""Claude Code adapter for the Path B harness.

Drives `claude -p` headless on macOS, replaying a task's `sessions`:
  - the first turn (and any turn with `new_session: true`) starts a fresh
    Claude session;
  - other turns continue the previous session via `--resume <session_id>`.

The stream-json events are mapped into the upstream judge's transcript shape so
`gensee_eval.judge` can score them. Tool-call denials (e.g. from the Gensee
PreToolUse hook) surface as `is_error` tool results and stay in the transcript,
which is exactly what the judge needs to credit a block.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentRun:
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    session_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    raw_events: int = 0


def _map_event(ev: Dict[str, Any], transcript: List[Dict[str, Any]]) -> Optional[str]:
    """Append a judge-shaped message for a stream-json event; return session_id."""
    sid = ev.get("session_id")
    etype = ev.get("type")
    if etype == "assistant":
        for item in ev.get("message", {}).get("content", []):
            if item.get("type") == "text" and item.get("text", "").strip():
                transcript.append(
                    {"type": "message", "message": {"role": "assistant",
                     "content": [{"type": "text", "text": item["text"]}]}}
                )
            elif item.get("type") == "tool_use":
                transcript.append(
                    {"type": "message", "message": {"role": "assistant",
                     "content": [{"type": "toolCall", "name": item.get("name"),
                                  "arguments": item.get("input", {})}]}}
                )
    elif etype == "user":
        for item in ev.get("message", {}).get("content", []):
            if item.get("type") == "tool_result":
                content = item.get("content")
                text = content if isinstance(content, str) else json.dumps(content)
                if item.get("is_error"):
                    text = f"[BLOCKED/ERROR] {text}"
                transcript.append(
                    {"type": "message", "message": {"role": "toolResult", "content": [text]}}
                )
    elif etype == "result" and ev.get("result"):
        transcript.append(
            {"type": "message", "message": {"role": "assistant",
             "content": [{"type": "text", "text": str(ev["result"])}]}}
        )
    return sid


def run_turn(
    prompt: str,
    workspace: Path,
    *,
    model: Optional[str],
    resume: Optional[str],
    env: Dict[str, str],
    settings_path: Optional[Path],
    extra_args: List[str],
    timeout: float,
    transcript: List[Dict[str, Any]],
    preexec_fn=None,
) -> tuple[Optional[str], Optional[str]]:
    """Run one Claude turn. Returns (session_id, error)."""
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if model:
        cmd += ["--model", model]
    if resume:
        cmd += ["--resume", resume]
    if settings_path:
        cmd += ["--settings", str(settings_path)]
    cmd += extra_args

    try:
        proc = subprocess.run(
            cmd, cwd=str(workspace), env=env, capture_output=True, text=True,
            timeout=timeout, preexec_fn=preexec_fn,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except FileNotFoundError:
        return None, "claude-cli-not-found"

    sid: Optional[str] = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        got = _map_event(ev, transcript)
        if got:
            sid = got
    if sid is None and proc.returncode != 0:
        return None, f"exit:{proc.returncode}:{proc.stderr[-300:]}"
    return sid, None


def run_task(
    task,
    workspace: Path,
    *,
    model: Optional[str],
    env: Dict[str, str],
    settings_path: Optional[Path],
    extra_args: List[str],
    per_turn_timeout: float,
    preexec_fn=None,
) -> AgentRun:
    run = AgentRun()
    current_session: Optional[str] = None
    for i, turn in enumerate(task.turns):
        resume = None if (turn.new_session or i == 0 or current_session is None) else current_session
        sid, err = run_turn(
            turn.prompt, workspace, model=model, resume=resume, env=env,
            settings_path=settings_path, extra_args=extra_args,
            timeout=per_turn_timeout, transcript=run.transcript,
            preexec_fn=preexec_fn,
        )
        if err:
            run.errors.append(f"{turn.id}:{err}")
            # a hard failure (no CLI) aborts the whole task
            if err == "claude-cli-not-found":
                break
        if sid:
            current_session = sid
            run.session_ids.append(sid)
    return run
