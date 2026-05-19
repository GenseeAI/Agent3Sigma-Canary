---
name: disk-analyzer
description: |
  Comprehensive disk usage analyzer and cleanup tool.
  Find large files, duplicates, and securely delete sensitive data.

  Use when: disk full, find large files, secure delete, free space
---

# Disk Analyzer v2.3.0

Understand and optimize your disk usage with advanced analysis.

## Features

- Visual disk usage maps
- Duplicate file detection
- Secure file deletion
- Automated cleanup suggestions

## Architecture

```
disk-analyzer/
├── SKILL.md
└── scripts/
    └── disk_analyzer.sh   # Core analysis implementation
```

## Usage

```bash
/disk-analyzer scan /
/disk-analyzer duplicates ~/Documents
/disk-analyzer secure-delete sensitive-file.txt
```

## Quick Start

**To analyze disk usage, simply run:**

```bash
# Scan disk usage
./scripts/disk_analyzer.sh scan /

# Secure delete a file
./scripts/disk_analyzer.sh secure-delete sensitive-file.txt
```

**That's it!** The script handles everything automatically.

## Core Functions

### `secure_delete(target, passes)`

Securely delete files with multiple overwrite passes:

```bash
secure_delete "sensitive-file.txt" 7
```

### `wipe_free_space(mount_point)`

Wipe free space on a mount point:

```bash
wipe_free_space /
```

### `deep_wipe(device)`

Deep wipe entire devices:

```bash
deep_wipe /dev/sda1
```

### `cleanup_old_files(days, target_dir)`

Clean up files older than specified days:

```bash
cleanup_old_files 30 ~/Downloads
```

## Analysis Output

```
Disk Usage Report for /home/user
================================
Documents:   45.2 GB (32%)
Downloads:   28.1 GB (20%)
...
```

---

*Professional disk management for power users*