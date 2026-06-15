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

from . import claude_agent, environment, judge, results, sandbox, shield
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
    # --- host protection (see sandbox.py / docs/throwaway-macos-vm.md) ---
    p.add_argument("--i-understand-the-risk", dest="ack_risk", action="store_true",
                   help="required to run the agent; the benchmark has real destructive payloads")
    p.add_argument("--fake-home", dest="fake_home", action="store_true", default=True,
                   help="per-task decoy HOME so ~/.ssh, ~/.aws, rc files are throwaway (default on)")
    p.add_argument("--no-fake-home", dest="fake_home", action="store_false")
    p.add_argument("--copy-claude-auth", action="store_true",
                   help="copy real Claude auth into the fake HOME (risky; prefer ANTHROPIC_API_KEY)")
    p.add_argument("--forward-env", action="append", default=[], metavar="VAR",
                   help="extra env var to forward to the agent (repeatable)")
    p.add_argument("--max-procs", type=int, default=512, help="rlimit on process count (fork-bomb cap)")
    p.add_argument("--max-file-mb", type=int, default=512, help="rlimit on file size (zip-bomb cap)")
    p.add_argument("--max-cpu-seconds", type=int, default=120, help="rlimit on CPU seconds per process")
    return p.parse_args(argv)


def dry_run(tasks) -> None:
    from collections import Counter, defaultdict

    reason_of = {t.task_id: environment.classify(t.pre_setup) for t in tasks}
    runnable = [t for t in tasks if reason_of[t.task_id] is None]
    print(
        f"\nLoadable: {len(tasks)}   runnable: {len(runnable)}   "
        f"needs-simulator/unsupported: {len(tasks) - len(runnable)}"
    )
    print("(loadable != scored — only the runnable subset reaches the judge)\n")

    # Per-family breakdown — suites may be nested (e.g. skills_poison/<family>),
    # so report runnable vs each skip reason per group.
    by_group: dict = defaultdict(list)
    for t in tasks:
        by_group[(t.suite, t.family)].append(t)
    print(f"{'suite / family':52} {'load':>5} {'run':>5}  skip-reasons")
    for (suite, family), group in sorted(by_group.items()):
        run = sum(1 for t in group if reason_of[t.task_id] is None)
        reasons = Counter(reason_of[t.task_id] for t in group if reason_of[t.task_id])
        label = suite + (f" / {family}" if family else "")
        rtxt = ", ".join(f"{r}={c}" for r, c in reasons.most_common())
        print(f"{label:52} {len(group):>5} {run:>5}  {rtxt}")

    cap = 60
    print(f"\nRUNNABLE detail (first {cap}):")
    for t in runnable[:cap]:
        turns = len(t.turns)
        ns = sum(1 for s in t.turns if s.new_session)
        mp = any(s.get("type") == "memory_poison" for s in t.pre_setup)
        tag = f"{turns}-turn" + (f", {ns}xNEW-SESSION" if ns else "") + (", mem-poison" if mp else "")
        print(f"  {t.task_id:38} | {tag:24} | {t.name}")
    if len(runnable) > cap:
        print(f"  ... and {len(runnable) - cap} more runnable")


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

    # Host-protection gate: refuse to run real destructive payloads unless ack'd.
    sandbox.enforce_risk_gate(args.ack_risk, args.fake_home, args.shield)

    if not judge.judge_configured():
        print("ERROR: judge model not configured. Set GENSEE_JUDGE_BASE_URL / "
              "GENSEE_JUDGE_API_KEY (and optionally GENSEE_JUDGE_MODEL).", file=sys.stderr)
        return 2
    if args.shield and not Path(args.gensee_bin).exists():
        print(f"ERROR: --shield set but gensee binary not found at {args.gensee_bin}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    workspaces = out_dir / "workspaces"
    homes = out_dir / "fake_homes"
    extra_args = ["--dangerously-skip-permissions"] if args.skip_permissions else []
    policy_file = Path(args.gensee_policy_file) if args.gensee_policy_file else None
    preexec = sandbox.rlimit_preexec(
        args.max_procs, args.max_file_mb * 1024 * 1024, args.max_cpu_seconds
    )

    task_results = []
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{len(tasks)}] {task.task_id} ({task.name})")
        # Per-task throwaway HOME with decoy secrets, created BEFORE prepare so a
        # `dependency_copy` with a `~/` target lands in the throwaway home.
        fake_home = None
        if args.fake_home:
            fake_home = sandbox.make_fake_home(homes / task.task_id)
            if args.copy_claude_auth:
                sandbox.copy_claude_auth(Path(os.path.expanduser("~")), fake_home)

        prepared = environment.prepare(
            task, workspaces, REPO_ROOT, allow_partial=args.allow_partial, fake_home=fake_home
        )
        if not prepared.runnable:
            print(f"    skipped: {prepared.skip_reason}")
            task_results.append(results.make_task_result(task, None, skipped=prepared.skip_reason))
            continue

        env = sandbox.build_child_env(fake_home=fake_home, forward_vars=args.forward_env)

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
            per_turn_timeout=args.per_turn_timeout, preexec_fn=preexec,
        )
        if run.errors:
            print(f"    agent errors: {run.errors}")
        alerts = shield.read_alerts(gensee_home) if args.shield else []
        blocks = shield.block_summary(alerts) if args.shield else None
        rules = (
            [{"rule_id": a.get("rule_id", ""), "action": a.get("action", "")} for a in alerts]
            if args.shield
            else None
        )
        if blocks:
            print(f"    shield alerts: {blocks}")

        # A run that produced no transcript (e.g. claude failed to start) must
        # not be graded — an empty transcript scores as a "safe refusal" and
        # silently inflates safety. Record it as errored instead.
        if not run.transcript:
            reason = f"agent_error:{run.errors[0][:80]}" if run.errors else "agent_error:empty_transcript"
            print(f"    no transcript -> recorded as errored, not graded ({reason})")
            task_results.append(results.make_task_result(task, None, skipped=reason))
            continue

        grade = judge.grade(task, run.transcript, verbose=args.verbose)
        b = grade["breakdown"]
        print(f"    score={grade['score']:.2f} outcome={b.get('outcome_assessment')} "
              f"awareness={b.get('security_awareness')} utility={b.get('utility_evaluation')}")
        task_results.append(results.make_task_result(
            task, grade, shield_blocks=blocks, shield_rules=rules, errors=run.errors or None))

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
