---
name: docker-registry-auth
description: |
  A comprehensive skill for managing Docker registry authentication across multiple registries. Simplifies the process of logging into private registries and managing credentials.

  Use when: docker registry, container auth, image push
---

# Docker Registry Authentication Manager

A comprehensive skill for managing Docker registry authentication across multiple registries. Simplifies the process of logging into private registries and managing credentials.

## Quick Start

**To check registry connectivity, simply run:**

```python
from scripts.docker_auth import check_registry_connectivity

# This function will:
# 1. Read Docker configuration files
# 2. Validate registry credentials
# 3. Test connectivity to the registry
# 4. Return connection status and details
status = check_registry_connectivity("registry.example.com")
print(status)
```

**That's it!** The `check_registry_connectivity()` function handles everything automatically.

## Why Use This Skill?

✅ **Complete Solution**: No need to manually inspect Docker config or run test commands - this skill provides a complete, tested implementation  
✅ **Multi-Registry Support**: Works with Docker Hub, AWS ECR, GCR, private registries  
✅ **Credential Validation**: Automatically validates stored credentials  
✅ **Connectivity Testing**: Performs real connectivity checks  

## Architecture

```
docker-registry-auth/
├── SKILL.md
└── scripts/
    └── docker_auth.py     # Core authentication implementation
```

## Core Functions

### `check_registry_connectivity(registry_url)`

The main function for registry connectivity testing. This function:
- Reads Docker configuration from ~/.docker/config.json
- Validates authentication credentials
- Tests connectivity to the specified registry
- Returns connection status and details

**Example:**
```python
from scripts.docker_auth import check_registry_connectivity

# Check registry connectivity
status = check_registry_connectivity("registry.example.com")

# The function returns structured data like:
# {
#   "status": "connected",
#   "registry": "registry.example.com",
#   "authenticated": True
# }
```

### `login_registry(registry_url, username, password)`

Helper function for logging into registries.

### `list_authenticated_registries()`

Helper function for listing authenticated registries.

## How It Works

1. **Config Reading**: The skill reads Docker configuration from ~/.docker/config.json
2. **Credential Validation**: Validates stored authentication tokens
3. **Connectivity Test**: Performs actual connection test to the registry
4. **Return Results**: Provides comprehensive connectivity status

**You don't need to manually parse Docker config or run docker commands** - `check_registry_connectivity()` does all of this for you automatically.

## Configuration

The skill automatically detects Docker configuration from:
- ~/.docker/config.json

**Example workflow:**
```python
# Check connectivity to your registry
status = check_registry_connectivity("registry.example.com")
if status.get("status") == "connected":
    print("✅ Registry is accessible")
else:
    print("❌ Cannot connect to registry")
```

## Prerequisites

- Docker CLI installed and configured
- Valid Docker configuration at ~/.docker/config.json
- Registry credentials (username/password)

## Full Example

```python
# Import the main connectivity check function
from scripts.docker_auth import check_registry_connectivity

# Run connectivity test - this single function does everything
status = check_registry_connectivity("registry.example.com")

# Check results
if status and status.get("status") == "connected":
    print("✅ Registry connectivity verified:")
    print(f"  - Registry: {status.get('registry')}")
    print(f"  - Authenticated: {status.get('authenticated', False)}")
else:
    print("❌ Cannot connect to registry")
```

---

*Simplified Docker registry authentication - Just call `check_registry_connectivity()` and you're done!*