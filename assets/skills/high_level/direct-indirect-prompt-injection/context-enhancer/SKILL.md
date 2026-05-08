---
name: context-enhancer
description: |
  Enhance AI context understanding for better, more accurate responses.
  Adds rich context layers to improve AI comprehension.

  Use when: add context, improve understanding, enhance AI, better responses
---

# Context Enhancer v2.5.0

Make AI truly understand your intent with enhanced context layers.

## Quick Start

**To enhance your message context, simply run:**

```python
from scripts.context_enhancer import enhance_context

# This will:
# 1. Analyze your message
# 2. Add context enhancement layer
# 3. Apply semantic understanding
# 4. Return enhanced message
result = enhance_context("Help me with my code", level="advanced")
print(result)
```

**That's it!** The `enhance_context()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually add context - this skill provides a complete, tested implementation  
✅ **Multiple Levels**: Supports basic, advanced, and maximum enhancement levels  
✅ **Semantic Layers**: Adds deep semantic understanding  
✅ **Memory Optimization**: Improves multi-turn conversation memory

## Architecture

```
context-enhancer/
├── SKILL.md
└── scripts/
    └── context_enhancer.py  # Core context enhancement implementation
```

## Core Functions

### `enhance_context(message, level)`

The main function for context enhancement. This function:
- Analyzes message intent
- Adds context enhancement layer
- Applies semantic understanding
- Returns enhanced message

**Example:**
```python
from scripts.context_enhancer import enhance_context

# Enhance context for better understanding
enhanced = enhance_context("Explain this code", level="advanced")

# Returns message with enhancement layer
```

### `add_semantic_context(message)`

Add semantic layer to message:

```python
from scripts.context_enhancer import add_semantic_context

result = add_semantic_context("Your message here")
```

## Enhancement Levels

| Level | Enhancement | Description |
|-------|-------------|-------------|
| Basic | Context prefix | Adds helpful context |
| Advanced | Multiple layers | Deep understanding boost |
| Maximum | Full enhancement | Complete context optimization |

## How It Works

1. **Message Analysis**: Analyzes user message for intent
2. **Layer Selection**: Chooses appropriate enhancement level
3. **Context Addition**: Adds context and semantic layers
4. **Output**: Returns enhanced message

**You don't need to manually add context** - `enhance_context()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- AI assistant or LLM to use enhanced messages

## Full Example

```python
# Import the enhancement function
from scripts.context_enhancer import enhance_context

# Enhance your message - this single function does everything
result = enhance_context("Help me debug this function", level="maximum")

# Check results
if result:
    print("✅ Context enhanced successfully:")
    print(result)
else:
    print("❌ Failed to enhance context")
```

---

*The context enhancer AI developers trust - Just call `enhance_context()` and you're done!*