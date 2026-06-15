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
The Qwen OpenAI endpoint is the cluster forwarder reached via `kubectl
port-forward` (same access pattern `platform-analysis` uses). `../remote-llm-api`
(SSH reverse tunnel from the OpenClaw sandbox) is an alternative if the bench
host has no cluster creds.

## ⚠️ Shared production GPUs — throttle and run off-peak
This forwarder (`-n staging`, historical naming = the prod namespace) backs
**openclaw production** on the **same GPUs**. The minted batch token **bypasses
the forwarder's rate-limiting**, so nothing upstream protects prod from us —
high concurrency causes prod `TimeoutError`s. Therefore:
- Keep the agent run **sequential** (the harness already runs one `claude -p` at
  a time — do NOT parallelize tasks).
- Run **off-peak**.
- Keep the **judge** on a different backend (Opus 4.6), so it doesn't pile onto
  the same GPUs.

## 1. Reach the Qwen OpenAI endpoint (same pattern as platform-analysis)
```bash
# Port-forward the forwarder. Plain port-forward DROPS under load, so loop it:
nohup bash -c 'while true; do kubectl port-forward -n staging svc/forwarder 9105:9105; sleep 2; done' >/tmp/pf.log 2>&1 &
export QWEN_OPENAI_BASE="http://localhost:9105/forward/gensee-397b/v1"

# Mint a Fernet bearer (no static key). FERNET_KEY is in GCP Secret Manager.
export FERNET_KEY=$(gcloud secrets versions access latest --secret=gshield-prod --project=gensee-deep-research | python3 -c 'import sys,json;print(json.load(sys.stdin)["FERNET_KEY"])')
export GENSEE_API_KEY=$(python3 ../platform-analysis/scripts/mint_batch_token.py)

# Sanity-check (expect HTTP 200):
curl -sS -o /dev/null -w '%{http_code}\n' "$QWEN_OPENAI_BASE/chat/completions" \
  -H "Authorization: Bearer $GENSEE_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"Gensee/Qwen3.5-397B","messages":[{"role":"user","content":"ok"}],"max_tokens":5}'
```
(The `mint_batch_token` payload may expire — re-mint if a long run starts 401ing.)

## 2. Start the Anthropic shim
Reuses `QWEN_OPENAI_BASE` and `GENSEE_API_KEY` exported in step 1.
```bash
pip install 'litellm[proxy]'
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
