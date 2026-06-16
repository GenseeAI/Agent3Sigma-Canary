# Running the Path B eval in a throwaway macOS VM

The benchmark executes **real** destructive payloads (credential reads/exfil,
reverse shells, fork bombs, disk fills) and the harness runs Claude Code with
permission prompts disabled, so the agent's actions hit the host for real. The
in-harness mitigations (fake `HOME`, env allowlist, `rlimit` caps) reduce
local-host damage but do **not** contain network egress, and **baseline (no
`--shield`) runs have no protection at all**. Treat a disposable VM as the real
isolation boundary — the same role Docker plays in the upstream harness.

The goal: a fresh macOS guest with **no real credentials**, a **revertible
snapshot**, and **no/limited network egress**.

## 1. Create the VM

On Apple Silicon, any of these work (they all use Apple's Virtualization
framework under the hood):

- **UTM** (free, GUI) — `brew install --cask utm`, then "Virtualize → macOS" and
  point it at a macOS IPSW restore image.
- **Tart** (CLI, scriptable, good for repeatable runs):
  ```bash
  brew install cirruslabs/cli/tart
  tart create canary --from-ipsw=latest          # downloads a macOS image
  tart set canary --cpu 4 --memory 8192
  ```
- **Parallels / VMware Fusion** if you already have them.

Use a generic local account (e.g. `evaluser`). Do **not** sign into iCloud,
Keychain, GitHub, or copy any SSH/AWS keys into the guest.

## 2. Snapshot before each run

Revert after every run so a successful attack can't persist:

```bash
# Tart
tart clone canary canary-run            # run against the clone, delete after
# ... run the eval inside canary-run ...
tart delete canary-run

# UTM / Parallels / VMware: take a snapshot, run, then "Restore snapshot".
```

## 3. Restrict the network

The harness does not block egress, so an unblocked exfil task will make real
outbound connections. Options, most to least isolated:

- **No network** — disconnect the VM's NIC entirely. The judge API call is made
  from the **harness process**; if you run the harness on the host (not in the
  VM) you can keep the VM offline and only the agent needs Anthropic access —
  but Claude Code needs network to reach the model, so fully-offline isn't
  possible when the agent itself is in the VM.
- **Egress allowlist** — allow only `api.anthropic.com` (and your judge
  endpoint) and drop everything else. With Tart you can attach a host-only/NAT
  network and apply a `pf` rule inside the guest, or filter at the host firewall.
- **Disposable network + revert** — at minimum, snapshot before and revert
  after, and use throwaway credentials so an exfil leaks nothing real.

A blocked-egress guest also means exfil-style attacks fail to "succeed,"
which is the safe default for measuring the shield.

## 4. Set up inside the guest

```bash
# Toolchain
xcode-select --install                       # git, clang
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv (or use system python3 + pyyaml)
# Install Claude Code per https://claude.com/claude-code

# Throwaway credentials only
export ANTHROPIC_API_KEY="sk-ant-...throwaway..."     # agent auth
export GENSEE_JUDGE_BASE_URL="https://api.openai.com/v1"
export GENSEE_JUDGE_API_KEY="sk-...throwaway..."      # judge
export GENSEE_JUDGE_MODEL="gpt-4o"
export GENSEE_EVAL_ACK_RISK=1                          # acknowledge the risk

# Clone the fork + (for --shield) build agent-shield
git clone https://github.com/GenseeAI/Agent3Sigma-Canary.git
git -C Agent3Sigma-Canary checkout gensee-eval
# git clone https://github.com/GenseeAI/agent-shield.git
# cargo build -p gensee-crate-cli --manifest-path agent-shield/Cargo.toml
```

## 5. Run

```bash
cd Agent3Sigma-Canary

# Baseline (no shield) — only ever do this in the disposable VM:
python -m gensee_eval.run_eval --suite chain --i-understand-the-risk \
  --model claude-sonnet-4 --image official --output-dir results/baseline

# With agent-shield:
python -m gensee_eval.run_eval --suite chain --i-understand-the-risk \
  --model claude-sonnet-4 --shield \
  --gensee-bin ../agent-shield/target/debug/gensee \
  --image gensee --output-dir results/gensee
```

Copy the `results/` JSONs out of the guest (or to a shared folder), then
**revert the snapshot / delete the clone**.

## What the in-harness mitigations still give you

If you cannot use a VM for a quick, lower-risk **shield-on** smoke test, the
defaults (`--fake-home`, env allowlist, `--max-procs`/`--max-file-mb`/
`--max-cpu-seconds`) neutralize the local credential-read, shell-rc-persistence,
fork-bomb, and disk-fill vectors. They do **not** stop network exfil, and they
are not appropriate for baseline runs. When in doubt, use the VM.
