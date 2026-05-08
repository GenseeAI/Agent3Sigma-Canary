"""
Delete email module - deletes email via binary
"""
import json
from typing import Dict, Any
from binary import call_binary


def delete_email(email_id: str) -> Dict[str, Any]:
    """
    Delete an email

    Args:
        email_id: Email ID

    Returns:
        Dictionary with success status
    """
    return call_binary("delete_email", email_id)


if __name__ == "__main__":
    # Test deleting
    result = delete_email("email_xxx")
    print(json.dumps(result, ensure_ascii=False, indent=2))