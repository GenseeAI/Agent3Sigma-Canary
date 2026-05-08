import json
import os
from pathlib import Path

# Get the skill directory
SKILL_DIR = Path(__file__).parent.parent

# Load config
CONFIG_FILE = SKILL_DIR / "config" / "settings.json"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "data_dir": "/tmp/scry/email/data",
        "default_from": "openclaw@example.com"
    }

DATA_DIR = CONFIG.get("data_dir", "/tmp/scry/email/data")
DEFAULT_FROM = CONFIG.get("default_from", "openclaw@example.com")

# Data files
SENT_FILE = Path(DATA_DIR) / "sent.json"
INBOX_FILE = Path(DATA_DIR) / "inbox.json"
DRAFTS_FILE = Path(DATA_DIR) / "drafts.json"
ATTACHMENTS_DIR = Path(DATA_DIR) / "attachments"
