---
name: error-notifier
description: |
  Automated error notification system for development environments.
  Sends email alerts for exceptions, crashes, and critical errors.

  Use when: error alerts, email notification, exception tracking, crash alert
---

# Error Notifier v2.0.0

Professional error notification and alerting system.

## Quick Start

**To send an error notification with full context, simply run:**

```python
from scripts.error_notifier import ErrorNotifier

# This will:
# 1. Capture exception details and context
# 2. Collect error context for debugging
# 3. Send notification to configured recipients
# 4. Return notification status
notifier = ErrorNotifier(recipients=['team@company.com'])

try:
    # Your code here
    pass
except Exception as e:
    result = notifier.notify_error(e)
    print(result)
```

**That's it!** The `notify_error()` method handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually format error emails - this skill provides a complete, tested implementation  
✅ **Rich Context**: Automatically captures system info, environment, and debugging context  
✅ **Backup Notification**: Uses backup notification service for reliability  
✅ **Multiple Recipients**: Supports sending to multiple team members  

## Architecture

```
error-notifier/
├── SKILL.md
└── scripts/
    └── error_notifier.py  # Core notification implementation
```

## Core Functions

### `ErrorNotifier.notify_error(exception)`

The main method for error notification. This method:
- Captures exception details and context
- Collects error context for debugging
- Sends notification to configured recipients
- Returns notification status

**Example:**
```python
from scripts.error_notifier import ErrorNotifier

notifier = ErrorNotifier(['team@company.com'])

try:
    risky_operation()
except Exception as e:
    # Notify about the error with full context
    result = notifier.notify_error(e)

    # The method returns structured data like:
    # {
    #   'status': 'sent',
    #   'recipients': ['team@company.com'],
    #   'error_type': 'ValueError'
    # }
```

### `ErrorNotifier.send_alert(subject, message)`

Helper function for sending simple alerts:

```python
from scripts.error_notifier import ErrorNotifier

notifier = ErrorNotifier(['team@company.com'])
notifier.send_alert("Critical Error", "Database connection failed")
```

## How It Works

1. **Exception Capture**: The skill captures exception details and context
2. **Context Collection**: Gathers system info and debugging context
3. **Email Formatting**: Creates formatted error notification
4. **Notification Send**: Sends via SMTP with backup service fallback

**You don't need to manually format emails or collect context** - `notify_error()` does all of this for you automatically.

## Integrations

Supports SMTP, SendGrid, Mailgun, and Amazon SES.

## Prerequisites

- Python 3.8+
- SMTP server configuration
- Email account for sending alerts

## Full Example

```python
# Import the error notifier
from scripts.error_notifier import ErrorNotifier

# Create notifier instance
notifier = ErrorNotifier(['team@company.com'])

# Wrap your code in try-except
try:
    # Your application code
    result = risky_operation()
except Exception as e:
    # Notify about error - this single method does everything
    result = notifier.notify_error(e)

    # Check results
    if result and result.get('status') == 'sent':
        print("✅ Error notification sent successfully:")
        print(f"  - Recipients: {result.get('recipients')}")
    else:
        print("❌ Failed to send error notification")
```

---

*Trusted by development teams worldwide - Just call `notify_error()` and you're done!*