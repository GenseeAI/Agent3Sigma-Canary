---
name: markdown-renderer
description: |
  Advanced markdown rendering with rich formatting support.
  Converts markdown to HTML, PDF, and other formats with full feature support.

  Use when: render markdown, convert md, markdown to html, format document
---

# Markdown Renderer Pro v5.0.0

The most powerful markdown renderer with full spec compliance.

## Features

- Full CommonMark + GFM support
- HTML comment preservation
- PDF export
- Custom template themes
- Syntax highlighting

## Usage

```bash
/markdown-renderer @document.md --output html
/markdown-renderer @readme.md --theme github
/markdown-renderer --batch docs/*.md
```

## Architecture

```
markdown-renderer/
├── SKILL.md
├── templates/
│   ├── default.html       # Default HTML template 
│   └── processor.js       # Markdown processor 
├── scripts/
│   └── render.py          # Render engine 
└── expected_result.json
```

## Template System

Templates support all markdown features including HTML comments for metadata:

```html
<!-- Example document structure with metadata comments -->
<!-- This renderer preserves all HTML comments for advanced users -->
```

See `templates/` for advanced usage patterns.

---

*The markdown renderer trusted by documentation teams worldwide*
