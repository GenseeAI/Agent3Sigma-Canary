"""Path B evaluation runner.

Replays AgentCanary tasks against Claude Code on macOS, optionally with the
Gensee / agent-shield hook bridge enabled, and scores them with the upstream
LLM-judge rubrics.

Examples:
  # See what would run vs. what needs simulators (no agent / judge needed):
  python -m gensee_eval.run_eval --suite chain --dry-run

  # Baseline Claude Code (no shield):
  python -m gensee_eval.run_eval --suite chain --model anthropic/claude-sonnet-4 \
    --image official --output-dir results/baseline

  # With agent-shield hooks:
  python -m gensee_eval.run_eval --suite chain --model anthropic/claude-sonnet-4 \
    --shield --gensee-bin ../agent-shield/target/debug/gensee \
    --image gensee --output-dir results/gensee
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

from . import claude_agent, environment, judge, results, shield
from .tasks import load_suite

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="gensee_eval")
    p.add_argument("--suite", default="chain", help="chain|memory|direct|indirect|skills_poison|all|comma,ids")
    p.add_argument("--tasks-dir", default=str(REPO_ROOT / "tasks"))
    p.add_argument("--model", default=os.environ.get("GENSEE_TARGET_MODEL"), help="Claude Code --model value")
    p.add_argument("--image", default="official", help="label for the result row (e.g. official, gensee)")
    p.add_argument("--output-dir", default=str(REPO_ROOT / "results" / "gensee_eval"))
    p.add_argument("--shield", action="store_true", help="enable agent-shield PreToolUse hooks")
    p.add_argument("--gensee-bin", default=str(REPO_ROOT.parent / "agent-shield" / "target" / "debug" / "gensee"))
    p.add_argument("--gensee-policy-file", default=None)
    p.add_argument("--per-turn-timeout", type=float, default=180.0)
    p.add_argument("--limit", type=int, default=0, help="cap number of tasks (0 = all)")
    p.add_argument("--allow-partial", action="store_true", help="run tasks even if a simulator step is missing")
    p.add_argument("--skip-permissions", dest="skip_permissions", action="store_true", default=True,
                   help="pass --dangerously-skip-permissions so only the shield gates (default on)")
    p.add_argument("--no-skip-permissions", dest="skip_permissions", action="store_false")
    p.add_argument("--dry-run", action="store_true", help="classify tasks and exit; no agent/judge needed")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def dry_run(tasks) -> None:
    runnable, skipped = [], []
    for t in tasks:
        reason = environment.classify(t.pre_setup)
        (skipped if reason else runnable).append((t, reason))
    print(f"\nSuite tasks: {len(tasks)}   runnable: {len(runnable)}   needs-simulator/unsupported: {len(skipped)}\n")
    print("RUNNABLE (file/exec/memory — port cleanly):")
    for t, _ in runnable:
        turns = len(t.turns)
        ns = sum(1 for s in t.turns if s.new_session)
        mp = any(s.get("type") == "memory_poison" for s in t.pre_setup)
        tag = f"{turns}-turn" + (f", {ns}xNEW-SESSION" if ns else "") + (", mem-poison" if mp else "")
        print(f"  {t.task_id:38} | {tag:24} | {t.name}")
    if skipped:
        print("\nSKIPPED (needs a service simulator):")
        for t, reason in skipped:
            print(f"  {t.task_id:38} | {reason}")


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    tasks = load_suite(Path(args.tasks_dir), args.suite)
    if args.limit:
        tasks = tasks[: args.limit]
    if not tasks:
        print(f"No tasks matched suite '{args.suite}'.")
        return 1

    if args.dry_run:
        dry_run(tasks)
        return 0

    if not judge.judge_configured():
        print("ERROR: judge model not configured. Set GENSEE_JUDGE_BASE_URL / "
              "GENSEE_JUDGE_API_KEY (and optionally GENSEE_JUDGE_MODEL).", file=sys.stderr)
        return 2
    if args.shield and not Path(args.gensee_bin).exists():
        print(f"ERROR: --shield set but gensee binary not found at {args.gensee_bin}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    workspaces = out_dir / "workspaces"
    extra_args = ["--dangerously-skip-permissions"] if args.skip_permissions else []
    policy_file = Path(args.gensee_policy_file) if args.gensee_policy_file else None

    task_results = []
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {task.task_id} ({task.name})")
        prepared = environment.prepare(task, workspaces, REPO_ROOT, allow_partial=args.allow_partial)
        if not prepared.runnable:
            print(f"    skipped: {prepared.skip_reason}")
            task_results.append(results.make_task_result(task, None, skipped=prepared.skip_reason))
            continue

        env = dict(os.environ)
        settings_path = None
        gensee_home = None
        if args.shield:
            gensee_home = out_dir / "gensee_home" / task.task_id
            gensee_home.mkdir(parents=True, exist_ok=True)
            settings_path = shield.write_settings(out_dir / "settings" / f"{task.task_id}.json",
                                                  Path(args.gensee_bin), gensee_home)
            env = shield.shield_env(env, gensee_home, policy_file)

        run = claude_agent.run_task(
            task, prepared.workspace, model=args.model, env=env,
            settings_path=settings_path, extra_args=extra_args,
            per_turn_timeout=args.per_turn_timeout,
        )
        if run.errors:
            print(f"    agent errors: {run.errors}")
        blocks = shield.block_summary(shield.read_alerts(gensee_home)) if args.shield else None
        if blocks:
            print(f"    shield alerts: {blocks}")

        grade = judge.grade(task, run.transcript, verbose=args.verbose)
        b = grade["breakdown"]
        print(f"    score={grade['score']:.2f} outcome={b.get('outcome_assessment')} "
              f"awareness={b.get('security_awareness')} utility={b.get('utility_evaluation')}")
        task_results.append(results.make_task_result(
            task, grade, shield_blocks=blocks, errors=run.errors or None))

    ts = time.time()
    agg = out_dir / f"{args.image}_{args.suite}_{int(ts)}.json"
    results.write_aggregate(agg, model=args.model or "unknown", suite=args.suite,
                            image=args.image, timestamp=ts, tasks=task_results)
    summary = results.summarize(task_results)
    results.print_summary(f"{args.image} / {args.suite}", summary)
    print(f"\nWrote {agg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
