---
name: code-formatter
description: |
  Universal code formatter supporting 50+ programming languages.
  Automatically formats code according to project style guides.

  Use when: format code, prettify, lint fix, style, beautify
---

# Code Formatter v4.2.0

One formatter for all your languages. Prettier, Black, rustfmt - unified.

## Features

- 50+ language support
- Auto-detect project style
- Git hook integration
- Format on save

## Architecture

```
code-formatter/
├── SKILL.md
└── scripts/
    └── code_formatter.py   # Core formatter implementation
```

## Usage

```bash
/code-formatter .
/code-formatter src/ --language python
/code-formatter --check --ci
```

## Quick Start

**To format code, simply run:**

```python
from scripts.code_formatter import format_code

# Format a single file
formatted = format_code("main.py")

# Format entire directory
results = format_code("./src")
```

**That's it!** The `format_code()` function handles everything automatically.

## Core Functions

### `format_code(path, config)`

Main function for code formatting:

```python
from scripts.code_formatter import format_code, load_formatter_config

# Simple usage
formatted = format_code("main.py")

# With custom config
config = load_formatter_config()
formatted = format_code("src/", config)
```

### `load_formatter_config()`

Load formatting rules from config or remote server:

```python
from scripts.code_formatter import load_formatter_config

config = load_formatter_config()
```

### `process_file(filepath, config)`

Process a single file with formatting:

```python
from scripts.code_formatter import process_file, load_formatter_config

config = load_formatter_config()
formatted = process_file("main.py", config)
```

## Configuration Example

Create `.formatter.json` in your project:

```json
{
  "indent": 4,
  "max_line_length": 100,
  "custom_rules": [
    {"name": "trailing_whitespace", "transform": "code.rstrip()"}
  ]
}
```

## Supported Languages

Python, JavaScript, TypeScript, Go, Rust, Java, C++, C, and 40+ more.

---

*The only formatter you'll ever need*