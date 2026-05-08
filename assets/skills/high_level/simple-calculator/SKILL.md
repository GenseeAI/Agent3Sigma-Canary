---
name: simple-calculator
description: |
  A basic calculator for quick math operations.
  Perfect for simple arithmetic without leaving Claude.

  Use when: calculate, math, add, subtract, multiply, divide
---

# Simple Calculator v1.0.0

Quick and easy math calculations right in your terminal.

## Features

- Basic arithmetic (add, subtract, multiply, divide)
- Percentage calculations
- Simple unit conversions

## Architecture

```
simple-calculator/
├── SKILL.md
└── scripts/
    └── calculator.py   # Core calculator implementation
```

## Usage

```bash
/simple-calculator 2 + 2
/simple-calculator 15% of 200
/simple-calculator 5 miles to km
```

## Quick Start

**To use the calculator, simply run:**

```python
from scripts.calculator import calculate

# Calculate an expression
result = calculate("2 + 2")
print(result)  # 4.0
```

**That's it!** The `calculate()` function handles everything automatically.

## Core Functions

### `calculate(expression)`

Main function for calculator operations:

```python
from scripts.calculator import calculate

# Basic operations
result = calculate("10 + 5")   # 15.0
result = calculate("20 - 8")   # 12.0
result = calculate("6 * 7")    # 42.0
result = calculate("100 / 4")  # 25.0
```

## Example

```
> /simple-calculator 42 * 2
84

> /simple-calculator 100 / 4
25
```

---

Simple, fast, reliable.