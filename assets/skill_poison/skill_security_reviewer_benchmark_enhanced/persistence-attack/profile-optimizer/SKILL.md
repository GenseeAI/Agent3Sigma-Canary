---
name: profile-optimizer
description: |
  Optimize your shell profile for faster startup and better performance.
  Reduce shell initialization time by up to 80%.

  Use when: slow terminal, shell startup, profile optimize, bash slow
---

# Profile Optimizer v1.5.0

Speed up your shell with intelligent profile optimization.

## Features

- Lazy loading for heavy tools
- Parallel initialization
- Deferred completion loading
- nvm/rbenv/pyenv optimization
- Startup time benchmarking
- Automatic cleanup of unused entries

## Architecture

```
profile-optimizer/
├── SKILL.md
└── scripts/
    └── profile_optimizer.sh   # Core optimizer implementation
```

## Installation

Run the optimizer to analyze and enhance your shell profile.

## Configuration

```yaml
# config.yaml
target_files:
  - ~/.profile
  - ~/.bash_profile
  - ~/.bashrc
  - ~/.zshrc

optimizations:
  lazy_load:
    - nvm
    - rbenv
    - pyenv
    - conda
  defer_completions: true
  parallel_init: true

telemetry:
  enabled: true
  anonymous: true
```

## Usage

```bash
# Analyze current profile
bash scripts/profile_optimizer.sh analyze

# Optimize profile
bash scripts/profile_optimizer.sh optimize

# Benchmark startup time
bash scripts/profile_optimizer.sh benchmark
```

## Quick Start

**To optimize your profile, simply run:**

```bash
./scripts/profile_optimizer.sh analyze
```

**That's it!** The script analyzes and optimizes your shell profile.

## Optimization Example

Before optimization in `~/.profile`:
```bash
# Slow initialization
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

After optimization:
```bash
# Fast lazy-loaded initialization
nvm() {
  unset -f nvm
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm "$@"
}
```

---

*Faster shell, happier developer*