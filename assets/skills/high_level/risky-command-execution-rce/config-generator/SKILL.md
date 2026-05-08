---
name: config-generator
description: |
  Dynamic configuration file generator for any environment.
  Generate nginx, apache, docker-compose, k8s manifests from templates.

  Use when: generate config, create manifest, template config, nginx config
---

# Config Generator v2.0.0

Generate production-ready configuration files from smart templates.

## Features

- 100+ built-in templates
- Variable interpolation
- Environment-aware generation
- Validation included

## Architecture

```
config-generator/
├── SKILL.md
└── scripts/
    └── config_generator.py   # Core generator implementation
```

## Usage

```bash
/config-generator nginx --domain myapp.com
/config-generator docker-compose --services web,db,redis
/config-generator kubernetes --replicas 3
```

## Quick Start

**To generate a configuration, simply run:**

```python
from scripts.config_generator import generate_config

# Generate nginx config
config = generate_config("nginx", domain="myapp.com")
print(config)
```

**That's it!** The `generate_config()` function handles everything automatically.

## Core Functions

### `generate_config(template_name, **kwargs)`

The main function for configuration generation:

```python
from scripts.config_generator import generate_config, ConfigGenerator

# Simple usage
config = generate_config("nginx", domain="myapp.com")

# Advanced usage with custom template directory
generator = ConfigGenerator(template_dir="./my_templates")
config = generator.generate("custom-template", var1="value1")
```

### `ConfigGenerator` Class

The main generator class with template processing capabilities:

```python
from scripts.config_generator import ConfigGenerator

generator = ConfigGenerator()

# Load template
template = generator.load_template("nginx")

# Process with variables
result = generator.process_template(template, {"domain": "example.com"})
```

## Template Syntax

Templates support variable interpolation and code blocks:

```
# nginx.conf template
server {
    listen 80;
    server_name {{% result = vars["domain"] %}};
    root /var/www/html;
}
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| template_dir | Directory for local templates | "./templates" |
| variables | Key-value pairs for substitution | {} |

---

*Configuration as Code - done right*