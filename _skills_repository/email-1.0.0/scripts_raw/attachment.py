"""
Attachment module - gets email attachments via binary
"""
import json
from typing import Dict, Any
from binary import call_binary


def get_attachments(email_id: str) -> Dict[str, Any]:
    """
    Get email attachments

    Args:
        email_id: Email ID

    Returns:
        Dictionary with success status and attachment list
    """
    return call_binary("get_attachments", email_id)


if __name__ == "__main__":
    # Test getting attachments
    result = get_attachments("email_xxx")
    print(json.dumps(result, ensure_ascii=False, indent=2))