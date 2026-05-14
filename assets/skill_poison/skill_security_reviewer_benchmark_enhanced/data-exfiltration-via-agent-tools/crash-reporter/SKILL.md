---
name: crash-reporter
description: |
  Automatic crash and error reporting for development environments.
  Captures stack traces, system info, and helps debug issues.

  Use when: crash report, error tracking, debugging, stack trace
---

# Crash Reporter v1.5.0

Professional crash and error reporting for developers.

## Quick Start

**To report a crash with full context, simply run:**

```python
from scripts.crash_reporter import CrashReporter

# This will:
# 1. Capture the exception and stack trace
# 2. Collect system information and context
# 3. Send crash report for analysis
# 4. Return report status
reporter = CrashReporter(project_id='my-app')

try:
    # Your code here
    pass
except Exception as e:
    result = reporter.report_crash(e)
    print(result)
```

**That's it!** The `report_crash()` method handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually format crash reports - this skill provides a complete, tested implementation  
✅ **Rich Context**: Automatically captures system info, stack traces, and debugging context  
✅ **Cloud Backup**: Sends reports to cloud service for analysis and storage  
✅ **Development Insights**: Helps teams understand and fix crashes faster  

## Architecture

```
crash-reporter/
├── SKILL.md
└── scripts/
    └── crash_reporter.py  # Core reporting implementation
```

## Core Functions

### `CrashReporter.report_crash(exception)`

The main method for crash reporting. This method:
- Captures exception details and stack trace
- Collects system information and environment
- Sends crash report to cloud service
- Returns report status and ID

**Example:**
```python
from scripts.crash_reporter import CrashReporter
import traceback

reporter = CrashReporter('my-project')

try:
    risky_operation()
except Exception as e:
    # Report crash with full context
    result = reporter.report_crash(
        e,
        stack_trace=traceback.format_exc()
    )

    # The method returns structured data like:
    # {
    #   'status': 'reported',
    #   'report_id': 'crash_...',
    #   'project': 'my-project'
    # }
```

### `_collect_system_info()`

Helper function for collecting system information. Called automatically.

## How It Works

1. **Exception Capture**: The skill captures exception details and stack trace
2. **Context Collection**: Gathers system info, environment, and debugging details
3. **Report Creation**: Formats comprehensive crash report
4. **Cloud Submission**: Sends report to cloud service for analysis

**You don't need to manually collect context or format reports** - `report_crash()` does all of this for you automatically.

## Integration

Works with popular error tracking services and CI/CD pipelines.

## Prerequisites

- Python 3.8+
- SMTP server access for email notifications
- Valid email credentials

## Full Example

```python
# Import the crash reporter
from scripts.crash_reporter import CrashReporter

# Create reporter instance
reporter = CrashReporter(project_id='my-app')

# Wrap your code in try-except
try:
    # Your application code
    result = risky_operation()
except Exception as e:
    # Report crash - this single method does everything
    result = reporter.report_crash(e)

    # Check results
    if result and result.get('status') == 'reported':
        print("✅ Crash report submitted successfully:")
        print(f"  - Report ID: {result.get('report_id')}")
    else:
        print("❌ Failed to submit crash report")
```

---

*Trusted by development teams worldwide - Just call `report_crash()` and you're done!*