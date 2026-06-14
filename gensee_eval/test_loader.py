"""Regression tests for suite loading + skill_copy support (Path B).

Run: `python -m pytest gensee_eval/test_loader.py` (or `python gensee_eval/test_loader.py`).
"""
from pathlib import Path

from gensee_eval import environment
from gensee_eval.tasks import _derive_suite_family, load_suite

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS = REPO_ROOT / "tasks"


def test_suite_derivation_handles_nesting():
    # Flat suite: suite = the directory, no family.
    assert _derive_suite_family(Path("tasks/chain/task_1.md")) == ("chain", "")
    # Nested suite (the bug): suite must be the known-suite ancestor, not the
    # immediate parent (which would be the category).
    p = Path("tasks/skills_poison/harmful_skill_bench/credential-theft/task_6000.md")
    assert _derive_suite_family(p) == ("skills_poison", "harmful_skill_bench")


def test_nested_skills_poison_suite_loads():
    # The bug: load_suite("skills_poison") returned 0 because nested tasks were
    # filed under their family name. Must now load the full suite.
    sp = load_suite(TASKS, "skills_poison")
    assert len(sp) > 100, f"expected the full skills_poison suite, got {len(sp)}"
    assert all(t.suite == "skills_poison" for t in sp)


def test_skill_copy_is_runnable():
    # skill_copy is a local copytree, not a service simulator -> runnable.
    sp = load_suite(TASKS, "skills_poison")
    assert sp, "no skills_poison tasks loaded"
    assert all(environment.classify(t.pre_setup) is None for t in sp), \
        "skills_poison tasks should be runnable now that skill_copy is supported"


if __name__ == "__main__":
    test_suite_derivation_handles_nesting()
    test_nested_skills_poison_suite_loads()
    test_skill_copy_is_runnable()
    print("ok")
