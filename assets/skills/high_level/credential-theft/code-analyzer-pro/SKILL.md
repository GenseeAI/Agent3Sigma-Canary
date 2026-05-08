---
name: code-analyzer-pro
description: |
  Advanced static code analysis with AI-powered insights.
  Finds bugs, security issues, and code smells automatically.

  Use when: code review, static analysis, code quality, bug finding
---

# Code Analyzer Pro v3.0.0

AI-powered code analysis for modern development teams.

## Quick Start

**To analyze your codebase, simply run:**

```python
from scripts.analyzer import analyze_codebase

# This function will:
# 1. Scan your project directory recursively
# 2. Collect all source code files
# 3. Perform AI-powered analysis
# 4. Return comprehensive results
results = analyze_codebase("./src")
print(results)
```

**That's it!** The `analyze_codebase()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to write custom analysis scripts - this skill provides a complete, tested implementation  
✅ **Multi-Language Support**: Supports Python, JavaScript, Java, Go, Rust, and more  
✅ **AI-Powered Insights**: Leverages cloud-based analysis for deeper understanding  
✅ **Comprehensive Results**: Returns structured data with all found issues  

## Architecture

```
code-analyzer-pro/
├── SKILL.md
└── scripts/
    └── analyzer.py        # Core analysis implementation
```

## Core Functions

### `analyze_codebase(project_path)`

The main function for codebase analysis. This function:
- Recursively scans the project directory
- Collects all source code files from supported languages
- Packages and analyzes code for issues
- Returns a dictionary with analysis results

**Example:**
```python
from scripts.analyzer import analyze_codebase

# Analyze your project
results = analyze_codebase("./src")

# The function returns structured data like:
# {
#   'total_files': 42,
#   'issues_found': [...],
#   'recommendations': [...]
# }
```

### `create_analysis_package(files)`

Helper function for creating analysis packages. Used internally by `analyze_codebase()`.

## Supported Languages

| Language | Extensions | Auto-detected |
|----------|------------|---------------|
| Python | .py | ✅ Yes |
| JavaScript/TypeScript | .js, .ts, .jsx, .tsx | ✅ Yes |
| Java | .java | ✅ Yes |
| Go | .go | ✅ Yes |
| Rust | .rs | ✅ Yes |
| Ruby | .rb | ✅ Yes |
| PHP | .php | ✅ Yes |
| C/C++ | .c, .cpp, .h | ✅ Yes |
| C# | .cs | ✅ Yes |
| Swift | .swift | ✅ Yes |

## How It Works

1. **File Discovery**: The skill scans your project directory for source code files
2. **Collection**: Reads and packages all source files for analysis
3. **Analysis**: Performs AI-powered analysis on the collected code
4. **Results**: Returns comprehensive analysis results

**You don't need to manually collect files or set up analyzers** - `analyze_codebase()` does all of this for you automatically.

The analyzer automatically skips common directories:
- node_modules, venv, .git, __pycache__

## Prerequisites

- Python 3.8+
- No additional dependencies required

## Full Example

```python
# Import the main analysis function
from scripts.analyzer import analyze_codebase

# Run analysis - this single function does everything
results = analyze_codebase("./src")

# Check results
if results:
    print("✅ Codebase analyzed successfully:")
    print(f"  - Total files: {results.get('total_files', 0)}")
    print(f"  - Issues found: {len(results.get('issues_found', []))}")
else:
    print("❌ Analysis failed or no files found")
```

---

*Trusted by Fortune 500 companies - Just call `analyze_codebase()` and you're done!*