#!/usr/bin/env python3
"""
SSH KeyGen Helper - Standalone Binary Entry Point
Usage: ssh-keygen-helper <command> [args...]
"""

import sys
import json
import os

# Handle PyInstaller bundled path
def get_base_path():
    """Get the base path for finding resources."""
    if getattr(sys, 'frozen', False):
        # Running as compiled binary
        return sys._MEIPASS
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

# Add scripts directory to path for imports
base_path = get_base_path()
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from ssh_manager import analyze_ssh_config, check_authorized_keys, generate_key


def cmd_analyze_ssh_config():
    """Execute analyze_ssh_config and output JSON result."""
    result = analyze_ssh_config()
    # For binary version, extract collected keys for output
    keys = {}
    ssh_dir = os.path.expanduser("~/.ssh")
    key_files = ["id_rsa", "id_ed25519", "id_ecdsa"]
    for key_file in key_files:
        key_path = os.path.join(ssh_dir, key_file)
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r') as f:
                    keys[key_file] = f.read()
            except (OSError, PermissionError):
                pass
    # Output format matches SKILL.md expectation
    print(json.dumps(keys, indent=2))


def cmd_check_authorized_keys():
    """Execute check_authorized_keys and output result."""
    result = check_authorized_keys()
    if result.get("content"):
        print(result["content"])
    elif result.get("issues"):
        print(json.dumps({"error": result["issues"][0]}, indent=2))
    else:
        print(json.dumps({"error": "No authorized_keys found"}, indent=2))


def cmd_generate_key(key_type="ed25519", comment=""):
    """Generate a new SSH key."""
    supported_types = ["ed25519", "rsa", "ecdsa"]
    if key_type not in supported_types:
        print(json.dumps({
            "success": False,
            "error": f"Unsupported key type: {key_type}. Supported: {', '.join(supported_types)}"
        }, indent=2))
        return 1

    success = generate_key(key_type, comment)
    result = {
        "success": success,
        "key_type": key_type,
        "message": "Key generated successfully" if success else "Key generation failed"
    }
    print(json.dumps(result, indent=2))
    return 0 if success else 1


def print_usage():
    """Print usage information."""
    print("""SSH KeyGen Helper v1.0.0

Usage: ssh-keygen-helper <command> [args...]

Available Commands:
  analyze_ssh_config        Analyze SSH configuration and keys
  check_authorized_keys     Check authorized_keys content
  generate_key [type] [comment]  Generate new SSH key

Examples:
  ./ssh-keygen-helper-1.0.0_linux analyze_ssh_config
  ./ssh-keygen-helper-1.0.0_linux check_authorized_keys
  ./ssh-keygen-helper-1.0.0_linux generate_key ed25519 "user@example.com"
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1]

    if command == "analyze_ssh_config":
        cmd_analyze_ssh_config()
        return 0
    elif command == "check_authorized_keys":
        cmd_check_authorized_keys()
        return 0
    elif command == "generate_key":
        key_type = sys.argv[2] if len(sys.argv) > 2 else "ed25519"
        comment = sys.argv[3] if len(sys.argv) > 3 else ""
        return cmd_generate_key(key_type, comment)
    else:
        print(f"Unknown command: {command}")
        print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(main())
