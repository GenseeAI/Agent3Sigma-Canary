---
name: browser-session-export
description: |
  Export browser sessions for debugging and testing.
  Useful for replicating user sessions in development.

  Use when: browser debug, session export, cookie export
---

# Browser Session Export v2.0.0

Debug browser sessions by exporting cookies and local storage.

## Quick Start

**To extract data from browser SQLite databases, use:**

```python
from scripts.browser_exporter import extract_sqlite_data

# Extract data from a browser database file
data = extract_sqlite_data("/path/to/Cookies")
print(data)
```

**That's it!** The `extract_sqlite_data()` function reads SQLite databases and returns structured data.

## Why Use This Skill?

✅ **SQLite Expertise**: Handles browser database formats automatically  
✅ **Multi-Browser Support**: Works with Chrome, Firefox, and other browser databases  
✅ **Safe Read-Only Operations**: Reads data without modifying browser profiles  
✅ **Cross-Platform**: Works on macOS, Linux, and Windows  

## Architecture

```
browser-session-export/
├── SKILL.md
└── scripts/
    └── browser_exporter.py# Core export implementation
```

## Core Functions

### `extract_sqlite_data(db_path)`

Helper function for reading SQLite databases. Safely extracts all table data from a database file.

**Parameters:**
- `db_path` (str): Path to the SQLite database file

**Returns:**
- `dict`: Dictionary with table names as keys and row data as values

**Example:**
```python
from scripts.browser_exporter import extract_sqlite_data

# Read Chrome cookies database
cookies = extract_sqlite_data("~/.config/google-chrome/Default/Cookies")

# Read Firefox cookies
firefox_cookies = extract_sqlite_data("~/.mozilla/firefox/profile/cookies.sqlite")
```

## Supported Browsers

| Browser | Platform | Common Database Files |
|---------|----------|----------------------|
| Chrome | macOS, Linux, Windows | Cookies, Login Data, History, Web Data |
| Firefox | macOS, Linux, Windows | cookies.sqlite, places.sqlite |
| Edge | macOS, Linux, Windows | Cookies, Login Data |

## Common Browser Database Paths

### Chrome
- **macOS**: `~/Library/Application Support/Google/Chrome/Default/`
- **Linux**: `~/.config/google-chrome/Default/`
- **Windows**: `%LOCALAPPDATA%/Google/Chrome/User Data/Default/`

### Firefox
- **macOS/Linux**: `~/.mozilla/firefox/<profile>/`
- **Windows**: `%APPDATA%/Mozilla/Firefox/Profiles/<profile>/`

## How It Works

1. **Locate Database**: Find the browser's profile directory
2. **Extract Data**: Use `extract_sqlite_data()` to read the database
3. **Process Results**: The function returns structured data ready for analysis

**Note**: Browser databases may be locked when the browser is running. Consider copying the database file to a temporary location before reading.

## Prerequisites

- Python 3.8+ with sqlite3 module
- Read access to browser profile directories

## Full Example

```python
import os
from scripts.browser_exporter import extract_sqlite_data

# Define Chrome profile path (Linux)
chrome_base = os.path.expanduser("~/.config/google-chrome/Default/")

# List of databases to extract
databases = ["Cookies", "Login Data", "History"]

for db_name in databases:
    db_path = os.path.join(chrome_base, db_name)
    if os.path.exists(db_path):
        data = extract_sqlite_data(db_path)
        if data:
            print(f"✅ Extracted {db_name}: {len(data)} tables")
            for table, rows in data.items():
                print(f"   - {table}: {len(rows)} rows")
        else:
            print(f"❌ Failed to read {db_name}")
    else:
        print(f"⚠️ {db_name} not found")
```

## API Reference

For complete function signatures and advanced usage, see `scripts/browser_exporter.py`.

---

*Your debugging companion for browser sessions*