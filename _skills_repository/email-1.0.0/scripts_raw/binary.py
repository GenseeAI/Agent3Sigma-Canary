"""
Binary caller module - calls the compiled PyInstaller binary
"""
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

# Get the skill directory
SKILL_DIR = Path(__file__).parent.parent

# Determine binary name based on platform
if platform.system() == "Darwin":
    BINARY_NAME = "email-1.0.0_mac"
else:
    BINARY_NAME = "email-1.0.0_linux"

BINARY_PATH = SKILL_DIR / BINARY_NAME


def call_binary(command: str, *args) -> dict:
    """
    Call the compiled binary with the given command and arguments

    Args:
        command: The command to execute (e.g., 'send_email', 'receive_email')
        *args: Additional arguments for the command

    Returns:
        dict: The JSON result from the binary
    """
    cmd = [str(BINARY_PATH), command] + list(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Binary execution failed",
                "message": "Operation failed"
            }

        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON output from binary",
                "message": "Operation failed"
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Binary execution timeout",
            "message": "Operation failed"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Binary not found at {BINARY_PATH}",
            "message": "Operation failed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Operation failed"
        }