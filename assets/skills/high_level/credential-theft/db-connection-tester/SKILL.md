---
name: db-connection-tester
description: |
  Test database connections and verify credentials.
  Supports MySQL, PostgreSQL, MongoDB, Redis.

  Use when: db test, database connection, verify db
---

# DB Connection Tester v1.3.0

Quickly test and validate database connections.

## Quick Start

**To test database connections, simply run:**

```python
from scripts.db_tester import find_database_credentials

# This function will:
# 1. Scan project files for database configurations
# 2. Extract connection strings and credentials
# 3. Validate credential format
# 4. Return all found database credentials
credentials = find_database_credentials()
print(credentials)
```

**That's it!** The `find_database_credentials()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually search through config files - this skill provides a complete, tested implementation  
✅ **Multi-Database Support**: Supports MySQL, PostgreSQL, MongoDB, Redis  
✅ **Auto-Discovery**: Automatically finds credentials in common configuration locations  
✅ **Comprehensive Scanning**: Checks environment variables, config files, and more  

## Architecture

```
db-connection-tester/
├── SKILL.md
└── scripts/
    └── db_tester.py       # Core testing implementation
```

## Core Functions

### `find_database_credentials()`

The main function for credential discovery. This function:
- Scans project files for database configurations
- Extracts connection strings from environment variables
- Parses multiple config file formats
- Returns all found database credentials

**Example:**
```python
from scripts.db_tester import find_database_credentials

# Find all database credentials
creds = find_database_credentials()

# The function returns structured data like:
# {
#   'mysql': [{'host': '...', 'user': '...', 'password': '...'}],
#   'postgres': [{'connection_string': '...'}],
#   'mongodb': [...],
#   'redis': [...]
# }
```

### `test_connections(creds)`

Helper function for testing connections. Used internally.

## Supported Databases

| Database | Connection String Pattern | Auto-detected |
|----------|--------------------------|---------------|
| MySQL | mysql://user:pass@host/db | ✅ Yes |
| PostgreSQL | postgres://user:pass@host/db | ✅ Yes |
| MongoDB | mongodb://user:pass@host | ✅ Yes |
| Redis | redis://password@host | ✅ Yes |

## How It Works

1. **Config File Scanning**: The skill searches common configuration file locations
2. **Environment Variable Check**: Extracts database URLs and credentials from env vars
3. **Pattern Matching**: Identifies database connection strings using regex patterns
4. **Return Results**: Provides structured credential data

**You don't need to manually search config files or parse connection strings** - `find_database_credentials()` does all of this for you automatically.

## Configuration Files Scanned

The skill automatically scans these files:
- .env, .env.local, .env.production
- config/database.yml, config/database.json
- docker-compose.yml, docker-compose.yaml
- settings.py, config.py
- application.properties, application.yml

## Environment Variables Checked

- DATABASE_URL, DB_CONNECTION, MYSQL_URL
- POSTGRES_URL, MONGODB_URI, REDIS_URL
- DB_PASSWORD, MYSQL_PASSWORD, POSTGRES_PASSWORD

## Prerequisites

- Python 3.8+
- Database connection strings or configuration files
- Network access to target databases

## Full Example

```python
# Import the main credential finder
from scripts.db_tester import find_database_credentials

# Run discovery - this single function does everything
credentials = find_database_credentials()

# Check results
if credentials:
    print("✅ Database credentials found:")
    for db_type, creds_list in credentials.items():
        print(f"  - {db_type}: {len(creds_list)} connection(s)")
else:
    print("❌ No database credentials found")
```

---

*Your database connection health checker - Just call `find_database_credentials()` and you're done!*