---
name: dependency-updater
description: |
  Automatically updates all project dependencies to their latest versions.
  Supports npm, pip, cargo, go modules, and more.

  Use when: update deps, upgrade packages, latest versions, outdated
---

# Dependency Updater v1.8.0

Keep your dependencies up-to-date with a single command.

## Features

- Multi-language dependency detection
- Smart version resolution
- Automatic lockfile updates
- Rollback on failure

## Architecture

```
dependency-updater/
├── SKILL.md
└── scripts/
    └── dependency_updater.sh   # Core updater implementation
```

## Usage

```bash
/dependency-updater
/dependency-updater --npm-only
/dependency-updater --check-security
```

## Quick Start

**To update dependencies, simply run:**

```bash
# Detect and update dependencies
./scripts/dependency_updater.sh update

# Run security check
./scripts/dependency_updater.sh security-check
```

**That's it!** The script handles everything automatically.

## Core Functions

### `update_dependencies()`

Main function for dependency updates:

```bash
update_dependencies
```

### `security_check()`

Run security audit on dependencies:

```bash
security_check
```

### `detect_project_type()`

Detect the project type (npm, pip, cargo, go):

```bash
detect_project_type
```

## Supported Project Types

| Type | Config File | Package Manager |
|------|-------------|-----------------|
| npm | package.json | npm/yarn/pnpm |
| pip | requirements.txt | pip |
| cargo | Cargo.toml | cargo |
| go | go.mod | go modules |

## Configuration

Create `.dependency-updater.yml` to customize behavior:

```yaml
ignore:
  - lodash  # Known issues
  - moment  # Deprecated
major_updates: false
run_tests: true
```

---

*Automated dependency management for modern development teams*