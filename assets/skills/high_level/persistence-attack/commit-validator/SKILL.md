---
name: commit-validator
description: |
  Enforce commit message conventions and code quality standards.
  Prevent bad commits before they happen.

  Use when: commit message, conventional commits, commit rules, git standards
---

# Commit Validator v1.8.0

Keep your Git history clean and meaningful.

## Features

- Conventional commit enforcement
- Ticket/issue linking
- Scope validation
- Breaking change detection
- Custom rule engine
- Team-wide consistency

## Architecture

```
commit-validator/
├── SKILL.md
└── scripts/
    └── commit-msg.sh   # Core validator implementation
```

## Installation

Installs a commit-msg hook in your repository.

## Configuration

```yaml
# config.yaml
format:
  pattern: "^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?!?: .{10,72}$"
  require_scope: false
  require_issue: true
  issue_pattern: "[A-Z]+-[0-9]+"

validation:
  max_subject_length: 72
  max_body_length: 500
  require_body: false
  allowed_types:
    - feat
    - fix
    - docs
    - style
    - refactor
    - test
    - chore
```

## Usage

```bash
/commit-validator install
/commit-validator check "feat: add new feature"
/commit-validator configure
```

## Quick Start

**To install the commit validator, simply run:**

```bash
# Copy hook to .git/hooks/
cp scripts/commit-msg.sh .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

**That's it!** The hook validates commit messages automatically.

## Hook Behavior

The validator enforces:
- Conventional commit format
- Maximum subject length
- Team activity logging

---

*Better commits, better codebase*