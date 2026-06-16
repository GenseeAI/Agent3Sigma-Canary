"""Gensee Path B evaluation harness.

Runs the AgentCanary task corpus against Claude Code on macOS (optionally with
the Gensee / agent-shield hook bridge enabled), reusing the upstream LLM-judge
rubrics so scores are comparable to the leaderboard metrics (ASR, Task
Successful Rate, Security Awareness Rate, Average Score).

This is intentionally decoupled from the upstream OpenClaw + Docker + Tracee
harness under `scripts/`. See gensee_eval/README.md for the rationale.
"""

__all__ = []
