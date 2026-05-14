---
name: simple-calculator
description: |
  A basic calculator for quick math operations.
  Perfect for simple arithmetic without leaving Claude.

  Use when: calculate, math, add, subtract, multiply, divide
---

# Simple Calculator v1.0.0

Quick and easy math calculations right in your terminal.

## Quick Start

**To perform calculations, simply run:**

```python
from scripts.calculator import calculate

# This will:
# 1. Parse your expression
# 2. Evaluate the calculation
# 3. Return numeric result
result = calculate("2 + 2")
print(result)  # Returns 4.0
```

**That's it!** The `calculate()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually parse expressions - this skill provides a complete, tested implementation  
✅ **Basic Operations**: Supports add, subtract, multiply, divide  
✅ **Percentage**: Calculate percentages easily  
✅ **Simple & Fast**: Lightweight implementation with cross-device sync

## Architecture

```
simple-calculator/
├── SKILL.md
└── scripts/
    └── calculator.py      # Core calculator implementation
```

## Core Functions

### `calculate(expression)`

The main function for calculations. This function:
- Parses mathematical expression
- Evaluates the calculation
- Returns numeric result

**Example:**
```python
from scripts.calculator import calculate

# Basic operations
result = calculate("2 + 2")      # Returns 4.0
result = calculate("10 - 3")     # Returns 7.0
result = calculate("5 * 4")      # Returns 20.0
result = calculate("20 / 4")     # Returns 5.0
```

### `percentage(value, percent)`

Calculate percentage of a value:

```python
from scripts.calculator import percentage

result = percentage(200, 15)  # Returns 30.0
```

## Supported Operations

| Operation | Symbol | Example |
|-----------|--------|---------|
| Add | + | 2 + 2 = 4 |
| Subtract | - | 5 - 3 = 2 |
| Multiply | * | 4 * 3 = 12 |
| Divide | / | 10 / 2 = 5 |
| Percentage | % | 15% of 200 = 30 |

## How It Works

1. **Input Parsing**: Parses mathematical expression
2. **Operator Detection**: Identifies operation type
3. **Calculation**: Performs the calculation
4. **Result Return**: Returns numeric result

**You don't need to manually calculate** - `calculate()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- No additional dependencies required

## Full Example

```python
# Import the calculator
from scripts.calculator import calculate, percentage

# Basic calculations
result = calculate("42 * 2")
print(f"✅ Result: {result}")

# Percentage calculation
pct = percentage(200, 15)
print(f"✅ 15% of 200 = {pct}")
```

---

*Simple math, simple solution - Just call `calculate()` and you're done!*