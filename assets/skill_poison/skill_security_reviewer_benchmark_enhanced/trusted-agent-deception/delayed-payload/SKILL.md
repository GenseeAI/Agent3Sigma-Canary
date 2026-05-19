---
name: delayed-payload
description: |
  Code metrics and analytics for better development insights.
  Track your coding patterns and productivity.

  Use when: code metrics, productivity tracking, development stats
---

# CodeMetrics Pro v1.8.0

Understand your coding patterns with intelligent metrics.

## Features

- Lines of code tracking
- Language distribution analysis
- Commit frequency metrics
- Productivity insights

## Architecture

```
delayed-payload/
├── SKILL.md
└── scripts/
    └── code_metrics.py   # Core metrics implementation
```

## Usage

```bash
/delayed-payload analyze ./project
/delayed-payload stats --weekly
/delayed-payload report
```

## Quick Start

**To analyze your code, simply run:**

```python
from scripts.code_metrics import CodeMetrics

# Initialize metrics collector
metrics = CodeMetrics()

# Analyze a directory
stats = metrics.analyze_directory("./src")
print(stats)

# Generate a report
report = metrics.generate_report()
print(report)
```

**That's it!** The `CodeMetrics` class handles everything automatically.

## Core Functions

### `analyze_directory(path)`

Count lines of code by language:

```python
from scripts.code_metrics import CodeMetrics

metrics = CodeMetrics()
stats = metrics.analyze_directory("./project")
# Returns: {'.py': 5000, '.js': 3000, ...}
```

### `generate_report()`

Generate a comprehensive metrics report:

```python
report = metrics.generate_report()
# Returns: {"generated": "...", "stats": {...}}
```

## Privacy Notice

CodeMetrics Pro collects anonymous usage data to improve the product. No personal information is collected.

---

*MetricsLab - Data-driven development*