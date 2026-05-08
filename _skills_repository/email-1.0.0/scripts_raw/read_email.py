"""
Read email module - reads email details via binary
"""
import json
from typing import Dict, Any
from binary import call_binary


def read_email(email_id: str) -> Dict[str, Any]:
    """
    Read email details

    Args:
        email_id: Email ID

    Returns:
        Dictionary with success status and email details
    """
    return call_binary("read_email", email_id)


if __name__ == "__main__":
    # Test reading
    result = read_email("email_xxx")
    print(json.dumps(result, ensure_ascii=False, indent=2))