# Running the benchmark against Gensee/Qwen3.5-397B

Why: the paper reports ~62% UOR for Qwen3.5-397B vs Sonnet's low — i.e. **real
headroom** where the shield's deterministic blocks can show a measurable ASR
reduction (on Sonnet the model defends on its own, so the shield can't move the
number). This wires Qwen as the **agent** so we can run control-vs-shielded on a
model that actually fails.

## Topology
```
[bench host] claude -p  --(Anthropic /v1/messages)-->  litellm shim (:4000)
   --(OpenAI /v1/chat/completions)-->  Qwen OpenAI endpoint
   -->  cluster forwarder (gensee-397b)  -->  Qwen3.5-397B
```
The Qwen OpenAI endpoint comes from `../remote-llm-api` (SSH reverse tunnel from
the OpenClaw sandbox) or a direct `kubectl port-forward` of the forwarder.

## 1. Expose the Qwen OpenAI endpoint
Either:
- **remote-llm-api tunnel** (existing): from the OpenClaw sandbox run the
  `remote-llm-api` skill (`init` + `start`); it exposes
  `http://59.49.77.70:8888/v1/chat/completions` (keyless edge).
- **kubectl port-forward** (if the bench host has cluster creds):
  `kubectl port-forward -n staging svc/forwarder 9105:9105`
  → `http://localhost:9105/forward/gensee-397b/v1`

Sanity-check it directly (OpenAI format):
```bash
curl "$QWEN_OPENAI_BASE/chat/completions" -H 'Content-Type: application/json' \
  -d '{"model":"Gensee/Qwen3.5-397B","messages":[{"role":"user","content":"hi"}],"max_tokens":16}'
```

## 2. Start the Anthropic shim
```bash
pip install 'litellm[proxy]'
export QWEN_OPENAI_BASE="http://59.49.77.70:8888/v1"   # or the port-forward URL
litellm --config gensee_eval/qwen_proxy/litellm_config.yaml --port 4000
```

## 3. SMOKE TEST FIRST — confirm tool-use survives the translation
Claude Code is tuned for Claude models; a non-Claude model via an
Anthropic↔OpenAI shim can mangle tool calls. Before any real run, confirm the
agent can issue a Bash tool call end-to-end:
```bash
ANTHROPIC_BASE_URL=http://localhost:4000 ANTHROPIC_AUTH_TOKEN=sk-anything \
  claude -p "run 'echo hello' with the Bash tool and report the output" \
  --model "Gensee/Qwen3.5-397B" --output-format stream-json --verbose --dangerously-skip-permissions
```
If you see a real `toolCall` for Bash + the output, the chain works. If it only
emits text (no tool calls), Qwen isn't producing OpenAI tool_calls through the
shim — stop here (see Caveats).

## 4. Run the benchmark (control vs shielded)
```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=sk-anything
export GENSEE_TARGET_MODEL="Gensee/Qwen3.5-397B"
# keep the JUDGE on a strong model (Opus 4.6 per the paper) via GENSEE_JUDGE_*

./run_suite.sh skills_poison        # or: chain, direct, or a task-id subset
```
`gensee_eval` forwards `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` into the agent
sandbox (sandbox._AUTH_FORWARD), and `--model` flows to `claude -p`.

## Caveats (important)
- **Fragile agent.** Claude Code + Qwen-via-shim may degrade tool use. The paper
  tested Qwen via **OpenClaw**, not Claude Code, so absolute ASR here will NOT
  match the paper. Smoke-test step 3 is mandatory.
- **The comparison is still valid.** Control vs shielded use the *same*
  Qwen-in-Claude-Code agent, so an ASR drop under `--shield` (with
  `deny-effective > 0`) is a real shield effect — which is the whole point.
- **The shield requires Claude Code** (it's a PreToolUse hook), so this shim is
  the only way to get Qwen *and* the shield in the same loop. Native OpenClaw
  would run Qwen faithfully but with no shield.
- **Egress.** The bench host must reach `QWEN_OPENAI_BASE`; the agent sandbox
  only needs `localhost:4000` (the shim) — keep the shim local to the bench host.
