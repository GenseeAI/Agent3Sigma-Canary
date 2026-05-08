import json
import platform
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

# Determine binary name based on platform
if platform.system() == "Darwin":
    BINARY_NAME = "bank_system-1.0.0_mac"
else:
    BINARY_NAME = "bank_system-1.0.0_linux"

BINARY_PATH = SKILL_DIR / BINARY_NAME

def call_binary(command: str, *args) -> dict:
    cmd = [str(BINARY_PATH), command] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr or "Binary execution failed", "message": "Operation failed"}
        return json.loads(result.stdout)
    except Exception as e:
        return {"success": False, "error": str(e), "message": "Operation failed"}