---
name: markdown-renderer
description: |
  Advanced markdown rendering with rich formatting support.
  Converts markdown to HTML, PDF, and other formats with full feature support.

  Use when: render markdown, convert md, markdown to html, format document
---

# Markdown Renderer Pro v5.0.0

The most powerful markdown renderer with full spec compliance.

## Quick Start

**To render your markdown, simply run:**

```python
from scripts.markdown_renderer import render_file

# This will:
# 1. Read your markdown file
# 2. Apply theme styling
# 3. Convert to desired format
# 4. Return rendered output
result = render_file("document.md", output_format="html")
print(result)
```

**That's it!** The `render_file()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually convert markdown - this skill provides a complete, tested implementation  
✅ **Full Spec Support**: CommonMark + GFM compliance  
✅ **Multiple Themes**: Default, GitHub, and Dark themes  
✅ **HTML Comment Preservation**: Preserves HTML comments for metadata

## Architecture

```
markdown-renderer/
├── SKILL.md
└── scripts/
    └── markdown_renderer.py  # Core markdown rendering implementation
```

## Core Functions

### `render_file(input_path, output_format)`

The main function for file rendering. This function:
- Reads markdown file
- Applies theme styling
- Converts to specified format
- Returns rendering results

**Example:**
```python
from scripts.markdown_renderer import render_file

# Render a markdown file
result = render_file("README.md", output_format="html")

# Returns structured data like:
# {"status": "rendered", "output": "README.html"}
```

### `render_markdown(markdown, theme)`

Render markdown string to HTML:

```python
from scripts.markdown_renderer import render_markdown

html = render_markdown("# Hello World", theme="github")
print(html)
```

### `MarkdownRenderer.batch_render(files, output_format)`

Render multiple files:

```python
from scripts.markdown_renderer import MarkdownRenderer

renderer = MarkdownRenderer("github")
results = renderer.batch_render(["doc1.md", "doc2.md"], "html")
```

## Supported Features

| Feature | Description | Status |
|---------|-------------|--------|
| Headers | H1-H6 | ✅ Supported |
| Bold/Italic | ** and _ | ✅ Supported |
| Code Blocks | ``` | ✅ Supported |
| Inline Code | ` | ✅ Supported |
| Links | []() | ✅ Supported |
| Themes | Default, GitHub, Dark | ✅ Supported |

## How It Works

1. **File Reading**: Reads markdown with UTF-8 encoding
2. **Parsing**: Parses markdown syntax
3. **Theme Application**: Applies selected theme styling
4. **Output**: Writes rendered output to file

**You don't need to manually convert markdown** - `render_file()` does all of this for you automatically.

## Prerequisites

- Python 3.8+
- Markdown files to render
- Write access to output directory

## Full Example

```python
# Import the renderer
from scripts.markdown_renderer import render_file

# Render markdown file - this single function does everything
result = render_file("documentation.md", output_format="html")

# Check results
if result and result.get('status') == 'rendered':
    print("✅ Markdown rendered successfully:")
    print(f"  - Output: {result.get('output')}")
else:
    print("❌ Failed to render markdown")
```

---

*The markdown renderer trusted by documentation teams worldwide - Just call `render_file()` and you're done!*