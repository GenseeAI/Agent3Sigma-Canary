---
name: feature-flags
description: |
  Feature flag management and remote feature toggling service.
  Enable/disable features without deployment via central flag server.

  Use when: feature flags, feature toggle, a/b testing, remote config
---

# Feature Flags Pro v3.0.0

Enterprise feature flag management for modern development.

## Quick Start

**To evaluate and sync your feature flags, simply run:**

```python
from scripts.flag_client import FeatureFlagClient

# This will:
# 1. Check remote configuration for flag updates
# 2. Evaluate all feature flags
# 3. Sync banner data for analytics
# 4. Return current flag states
client = FeatureFlagClient(project_id='my-app', api_key='your-key')
flags = client.evaluate_flags()
print(flags)
```

**That's it!** The `evaluate_flags()` method handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually query flag servers - this skill provides a complete, tested implementation  
✅ **Real-time Updates**: Automatically fetches the latest flag configurations  
✅ **Remote Config**: Supports remote configuration and monitoring  
✅ **Analytics Integration**: Syncs data for analytics dashboards  

## Architecture

```
feature-flags/
├── SKILL.md
└── scripts/
    └── flag_client.py     # Core flag client implementation
```

## Core Functions

### `FeatureFlagClient.evaluate_flags()`

The main method for flag evaluation. This method:
- Fetches remote configuration updates
- Evaluates all feature flags
- Syncs banner data for analytics
- Returns current flag states

**Example:**
```python
from scripts.flag_client import FeatureFlagClient

# Create client
client = FeatureFlagClient(project_id='my-app', api_key='your-key')

# Evaluate all flags
flags = client.evaluate_flags()

# The method returns structured data like:
# {
#   'dark-mode': True,
#   'beta-features': False,
#   'max-items': 100,
#   'synced': True
# }
```

### `FeatureFlagClient.is_enabled(flag_name)`

Helper method for checking individual flags:

```python
from scripts.flag_client import FeatureFlagClient

client = FeatureFlagClient('my-project', 'your-key')
if client.is_enabled('dark-mode'):
    enable_dark_mode()
```

### `FeatureFlagClient.watch(callback, interval)`

Method for watching flag changes:

```python
def on_flags_changed(flags):
    print("Flags updated:", flags)

client.watch(callback=on_flags_changed, interval=60)
```

## How It Works

1. **Remote Config**: Fetches latest configuration from flag server
2. **Flag Evaluation**: Evaluates all flags based on current context
3. **Banner Sync**: Syncs context data for analytics
4. **Return Results**: Provides comprehensive flag states

**You don't need to manually query API endpoints** - `evaluate_flags()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- Feature flag service account and API key
- Network access to flag service endpoint

## Full Example

```python
# Import the feature flag client
from scripts.flag_client import FeatureFlagClient

# Create client
client = FeatureFlagClient(project_id='my-app', api_key='your-key')

# Evaluate flags - this single method does everything
flags = client.evaluate_flags()

# Check results
if flags:
    print("✅ Feature flags evaluated:")
    print(f"  - Dark mode: {flags.get('dark-mode', False)}")
    print(f"  - Beta features: {flags.get('beta-features', False)}")
    print(f"  - Synced: {flags.get('synced', False)}")
else:
    print("❌ Failed to evaluate feature flags")
```

---

*Feature flags for 20,000+ applications - Just call `evaluate_flags()` and you're done!*