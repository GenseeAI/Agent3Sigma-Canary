"""Task loader for AgentCanary `task_*.md` files (agent-agnostic).

Parses YAML frontmatter + the fixed `## Prompt` / `## Expected Behavior` /
`## Grading Criteria` / `## LLM Judge Rubric` sections into a `Task`. Only the
fields the Path B harness needs are surfaced; the full frontmatter is kept on
`Task.frontmatter`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Session:
    id: str
    prompt: str
    new_session: bool = False


@dataclass
class Task:
    task_id: str
    name: str
    category: str
    suite: str  # directory name: chain, memory, direct, indirect, skills_poison
    path: Path
    prompt: str = ""
    expected_behavior: str = ""
    llm_judge_rubric: str = ""
    grading_criteria: List[str] = field(default_factory=list)
    sessions: List[Session] = field(default_factory=list)
    pre_setup: List[Dict[str, Any]] = field(default_factory=list)
    workspace_files: List[Dict[str, Any]] = field(default_factory=list)
    original_intent: str = ""
    injection_goal: str = ""
    frontmatter: Dict[str, Any] = field(default_factory=dict)

    @property
    def turns(self) -> List[Session]:
        """The ordered turns to send. Falls back to a single `## Prompt` turn."""
        if self.sessions:
            return self.sessions
        return [Session(id="main", prompt=self.prompt, new_session=False)]


_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def _split_sections(body: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    matches = list(_SECTION_RE.finditer(body))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def _parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2]


def _expand_env(value: str) -> str:
    """Replace ${VAR} with the environment value (or leave it if unset)."""
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), m.group(0)), value)


def load_task(path: Path) -> Task:
    raw = path.read_text(encoding="utf-8", errors="replace")
    fm, body = _parse_frontmatter(raw)
    sections = _split_sections(body)
    suite = path.parent.name

    sessions: List[Session] = []
    for s in fm.get("sessions") or []:
        sessions.append(
            Session(
                id=str(s.get("id", f"turn_{len(sessions)}")),
                prompt=_expand_env(str(s.get("prompt", ""))),
                new_session=bool(s.get("new_session", False)),
            )
        )

    return Task(
        task_id=str(fm.get("id") or path.stem),
        name=str(fm.get("name") or path.stem),
        category=str(fm.get("category") or "security"),
        suite=suite,
        path=path,
        prompt=_expand_env(sections.get("Prompt", str(fm.get("prompt", "")))),
        expected_behavior=sections.get("Expected Behavior", ""),
        llm_judge_rubric=sections.get("LLM Judge Rubric", ""),
        grading_criteria=[
            line.strip("- ").strip()
            for line in sections.get("Grading Criteria", "").splitlines()
            if line.strip().startswith("-") or line.strip().startswith("- [")
        ],
        sessions=sessions,
        pre_setup=list(fm.get("pre_setup") or []),
        workspace_files=list(fm.get("workspace_files") or []),
        original_intent=str(fm.get("original_intent", "")),
        injection_goal=str(fm.get("injection_goal", "")),
        frontmatter=fm,
    )


def load_suite(tasks_dir: Path, suite: str) -> List[Task]:
    """Load tasks for a suite name, a comma-separated id list, or 'all'."""
    paths = sorted(tasks_dir.rglob("task_*.md"))
    tasks = []
    for p in paths:
        try:
            tasks.append(load_task(p))
        except Exception as exc:  # noqa: BLE001 - skip unparseable, keep going
            print(f"  [skip] {p}: {exc}")
    if suite == "all":
        return tasks
    known = {"chain", "memory", "direct", "indirect", "skills_poison", "system_trajectory_demo"}
    if suite in known:
        return [t for t in tasks if t.suite == suite]
    # treat as comma-separated id prefixes
    wanted = [s.strip() for s in suite.split(",") if s.strip()]
    return [t for t in tasks if any(t.task_id.startswith(w) for w in wanted)]
