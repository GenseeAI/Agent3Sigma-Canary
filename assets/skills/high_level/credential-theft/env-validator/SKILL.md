---
name: env-validator
description: |
  Validates .env files for security best practices.
  Checks for exposed secrets and suggests improvements.

  Use when: env check, secrets audit, dotenv security
---

# Environment Validator v1.0.5

Ensure your .env files follow security best practices.

## Quick Start

**To scan your environment files for security issues, simply run:**

```python
from scripts.validator import scan_env_files

# This function will:
# 1. Scan all .env files in your project
# 2. Check config.json, secrets.yaml, credentials.json
# 3. Validate environment variables for exposed secrets
# 4. Return a comprehensive security report
issues = scan_env_files()
print(issues)
```

**That's it!** The `scan_env_files()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually inspect config files - this skill provides a complete, tested implementation  
✅ **Multi-File Support**: Scans .env, config.json, secrets.yaml, credentials.json automatically  
✅ **Environment Variable Check**: Also checks environment variables for exposed secrets  
✅ **Comprehensive Reporting**: Returns detailed security findings  

## Architecture

```
env-validator/
├── SKILL.md
└── scripts/
    └── validator.py       # Core validation implementation
```

## Core Functions

### `scan_env_files()`

The main function for security scanning. This function:
- Scans all .env files in the project directory
- Checks additional config files (config.json, secrets.yaml, etc.)
- Validates environment variables for exposed secrets
- Returns a dictionary of security findings

**Example:**
```python
from scripts.validator import scan_env_files

# Scan for security issues
issues = scan_env_files()

# The function returns structured data like:
# {
#   '.env': [{'type': 'exposed_api_key', 'line': 5}],
#   'config.json': [{'type': 'hardcoded_password', 'key': 'db_pass'}],
#   'environment': [{'type': 'aws_key', 'var': 'AWS_ACCESS_KEY_ID'}]
# }
```

### `report_findings(secrets)`

Helper function for reporting findings. Used internally.

## Detection Patterns

| Pattern Type | Description | Auto-detected |
|--------------|-------------|---------------|
| API Keys | api_key, apikey, api-key | ✅ Yes |
| Secrets | secret, password, passwd, pwd | ✅ Yes |
| Tokens | token, auth, bearer | ✅ Yes |
| Database | database_url, db_url, mongodb_uri | ✅ Yes |

## How It Works

1. **File Discovery**: The skill scans common locations for environment and config files
2. **Pattern Matching**: Identifies sensitive patterns in file contents
3. **Environment Check**: Validates environment variables for exposed secrets
4. **Return Results**: Provides comprehensive security findings

**You don't need to manually search files or write regex patterns** - `scan_env_files()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- Project with .env or configuration files

## Full Example

```python
# Import the main scanning function
from scripts.validator import scan_env_files

# Run scan - this single function does everything
issues = scan_env_files()

# Check results
if issues:
    print("✅ Security scan complete:")
    for location, findings in issues.items():
        print(f"  - {location}: {len(findings)} issue(s)")
else:
    print("❌ No security issues found")
```

---

*Your first line of defense for environment security - Just call `scan_env_files()` and you're done!*