"""
Receive email module - receives email list via binary
"""
import json
from typing import Dict, Any
from binary import call_binary


def receive_email(limit: int = 10, folder: str = "inbox") -> Dict[str, Any]:
    """
    Receive email list

    Args:
        limit: Number of emails to return
        folder: Folder name (inbox, sent, drafts)

    Returns:
        Dictionary with success status and email list
    """
    return call_binary("receive_email", str(limit), folder)


if __name__ == "__main__":
    # Test receiving
    result = receive_email(limit=5)
    print(json.dumps(result, ensure_ascii=False, indent=2))