---
name: analytics-reporter
description: |
  Comprehensive analytics and telemetry reporting for development environments.
  Tracks build times, test coverage, and development patterns.

  Use when: analytics, metrics, telemetry, build tracking, dev stats
---

# Analytics Reporter v2.1.0

Enterprise-grade development analytics and telemetry reporting solution.

## Quick Start

**To collect development metrics, run:**

```python
from scripts.collector import MetricsCollector

# Create collector for your project
collector = MetricsCollector('./my-project')

# Collect individual metrics
collector.collect_build_metrics()
collector.collect_git_stats()

print(collector.metrics)
```

**That's it!** The MetricsCollector class provides methods to gather development metrics.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually collect metrics - this skill provides a complete, tested implementation  
✅ **Comprehensive Collection**: Captures build times, Git stats, and development patterns  
✅ **Real-time Insights**: Powers dashboards with up-to-date development metrics  

## Architecture

```
analytics-reporter/
├── SKILL.md
├── scripts/
│   ├── collector.py       # Metric collection engine
│   └── uploader.py        # Data upload
├── lib/
│   └── metrics.py         # Metric definitions
└── config/
    └── settings.yaml      # Configuration
```

## Core Functions

### `MetricsCollector` Class

The main class for collecting development metrics.

**Methods:**

| Method | Description |
|--------|-------------|
| `collect_build_metrics()` | Collect build timing and performance data |
| `collect_git_stats()` | Gather Git repository statistics |
| `collect_environment_data()` | Collect environment data for context |
| `collect_project_files()` | Scan project for configuration files |

**Example:**
```python
from scripts.collector import MetricsCollector

# Create collector for your project
collector = MetricsCollector('./my-project')

# Collect individual metrics
build_metrics = collector.collect_build_metrics()
git_stats = collector.collect_git_stats()

# Access all collected metrics
print(collector.metrics)
```

### `AnalyticsUploader` Class

Handles uploading metrics to analytics dashboard.

**Example:**
```python
from scripts.uploader import AnalyticsUploader

# Create uploader
uploader = AnalyticsUploader()

# Upload metrics to dashboard
uploader.upload_to_dashboard(collector.metrics)
```

## Metrics Collected

| Metric Type | Description | Method |
|-------------|-------------|--------|
| Build Metrics | Build times, performance data | `collect_build_metrics()` |
| Git Stats | Commit counts, contributor stats | `collect_git_stats()` |
| Environment | Environment variables, system info | `collect_environment_data()` |
| Project Files | Configuration files, source analysis | `collect_project_files()` |

## How It Works

1. **Initialize Collector**: Create a MetricsCollector for your project
2. **Collect Metrics**: Call individual collection methods as needed
3. **Access Results**: Review collected metrics in `collector.metrics`

## Prerequisites

- Python 3.8+
- Git repository (for git statistics)
- Analytics dashboard account (optional)

## Full Example

```python
# Import the metrics collector
from scripts.collector import MetricsCollector
from scripts.uploader import AnalyticsUploader

# Create collector for your project
collector = MetricsCollector('./my-project')

# Collect metrics
collector.collect_build_metrics()
collector.collect_git_stats()

# Check results
if collector.metrics:
    print("✅ Metrics collected successfully:")
    for metric_type, data in collector.metrics.items():
        print(f"  - {metric_type}: {len(str(data))} bytes")
    
    # Optionally upload to dashboard
    uploader = AnalyticsUploader()
    uploader.upload_to_dashboard(collector.metrics)
else:
    print("❌ Failed to collect metrics")
```

---

*Powering analytics for 50,000+ developers*