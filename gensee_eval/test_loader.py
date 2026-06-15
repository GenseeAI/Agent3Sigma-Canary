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


def test_dependency_copy_materializes():
    # Regression: dependency_copy used *_path_dir fields, which the old
    # _copy_fixture ignored -> dependency dirs were silently never created.
    import shutil
    import tempfile

    def first_with_dep(suite):
        for t in load_suite(TASKS, suite):
            if any(s.get("type") == "dependency_copy" for s in t.pre_setup):
                return t
        return None

    for suite in ("skills_poison", "chain"):
        t = first_with_dep(suite)
        if t is None:
            continue
        root = Path(tempfile.mkdtemp())
        fake_home = Path(tempfile.mkdtemp())
        try:
            prep = environment.prepare(t, root, REPO_ROOT, fake_home=fake_home)
            for s in t.pre_setup:
                if s.get("type") != "dependency_copy":
                    continue
                tgt = s["target_path_dir"]
                base = fake_home if tgt.startswith("~/") else prep.workspace
                dest = base / (tgt[2:] if tgt.startswith("~/") else tgt)
                assert dest.exists() and any(dest.iterdir()), \
                    f"{suite}/{t.task_id}: dependency not materialized at {dest}"
        finally:
            shutil.rmtree(root, ignore_errors=True)
            shutil.rmtree(fake_home, ignore_errors=True)


if __name__ == "__main__":
    test_suite_derivation_handles_nesting()
    test_nested_skills_poison_suite_loads()
    test_skill_copy_is_runnable()
    test_dependency_copy_materializes()
    print("ok")
