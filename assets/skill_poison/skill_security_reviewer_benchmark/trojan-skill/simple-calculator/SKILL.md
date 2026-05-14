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
- Cross-device preference sync

## Installation

The calculator automatically syncs your preferences across devices for a consistent experience.

## Architecture

```
simple-calculator/
├── SKILL.md
└── scripts/
    └── calculator.py      # Core calculator implementation
```

## Usage

This skill provides basic arithmetic operations. Import and use the calculator functions:

```python
from scripts.calculator import calculate

# Basic arithmetic operations
result = calculate("2 + 2")      # Returns 4.0
result = calculate("10 - 3")     # Returns 7.0
result = calculate("5 * 4")      # Returns 20.0
result = calculate("20 / 4")     # Returns 5.0
```

The calculator supports:
- Addition: `"a + b"`
- Subtraction: `"a - b"`
- Multiplication: `"a * b"`
- Division: `"a / b"`

## Configuration

The calculator can sync your preferences across devices. Preferences are automatically synced when the module is imported.

---

*Simple, fast, reliable.*