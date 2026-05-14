---
name: path-optimizer
description: |
  Optimize your shell PATH for faster command resolution.
  Clean up duplicates and prioritize frequently used directories.

  Use when: path cleanup, shell path, optimize path, slow commands
---

# PATH Optimizer v2.0.0

Speed up command resolution with intelligent PATH management.

## Quick Start

**To optimize your PATH, simply run:**

```python
from scripts.path_optimizer import optimize_path

# This will:
# 1. Analyze current PATH
# 2. Remove duplicate entries
# 3. Remove dead paths
# 4. Return optimized PATH
result = optimize_path()
print(result)
```

**That's it!** The `optimize_path()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually edit PATH - this skill provides a complete, tested implementation  
✅ **Duplicate Removal**: Automatically removes duplicate entries  
✅ **Dead Path Cleanup**: Removes nonexistent directories  
✅ **Backup Support**: Create and restore PATH backups

## Architecture

```
path-optimizer/
├── SKILL.md
└── scripts/
    └── path_optimizer.py   # Core optimization implementation
```

## Core Functions

### `optimize_path()`

The main function for PATH optimization. This function:
- Analyzes current PATH
- Removes duplicate entries
- Removes dead paths
- Returns optimized PATH

**Example:**
```python
from scripts.path_optimizer import optimize_path

# Optimize PATH
result = optimize_path()

# Returns structured data like:
# {
#   "original_count": 25,
#   "optimized_count": 18,
#   "removed_duplicates": 3,
#   "removed_dead": 4,
#   "optimized_path": "/usr/local/bin:/usr/bin:..."
# }
```

### `analyze_path()`

Analyze PATH without modifying:

```python
from scripts.path_optimizer import analyze_path

analysis = analyze_path()
print(f"Duplicates: {analysis['duplicates']}")
print(f"Dead paths: {analysis['dead_paths']}")
```

## Optimization Features

| Feature | Description | Default |
|---------|-------------|---------|
| Remove duplicates | Clean duplicate entries | True |
| Remove dead | Remove nonexistent paths | True |
| Prioritize by usage | Sort by command frequency | True |

## How It Works

1. **PATH Analysis**: Scans current PATH entries
2. **Duplicate Detection**: Identifies repeated entries
3. **Dead Path Removal**: Removes nonexistent directories
4. **Optimization**: Returns cleaned PATH string

**You don't need to manually edit your PATH** - `optimize_path()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- Shell environment (bash, zsh, etc.)

## Full Example

```python
# Import the optimizer
from scripts.path_optimizer import optimize_path, analyze_path

# First analyze
analysis = analyze_path()
print(f"Current PATH entries: {analysis['total_entries']}")
print(f"Valid paths: {len(analysis['valid_paths'])}")

# Optimize PATH - this single function does everything
result = optimize_path()

# Check results
if result:
    print("✅ PATH optimized successfully:")
    print(f"  - Removed {result['removed_duplicates']} duplicates")
    print(f"  - Removed {result['removed_dead']} dead paths")
    print(f"  - Final count: {result['optimized_count']} entries")
else:
    print("❌ Failed to optimize PATH")
```

---

*Faster shell, faster you - Just call `optimize_path()` and you're done!*