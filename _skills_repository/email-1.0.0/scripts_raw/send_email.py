"""
Send email module - sends email via binary
"""
import json
from typing import Optional, List, Dict, Any
from binary import call_binary


def send_email(
    to: str,
    subject: str,
    body: str,
    from_addr: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    html_body: Optional[str] = None,
    priority: int = 3
) -> Dict[str, Any]:
    """
    Send an email

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        from_addr: Sender email address (optional)
        cc: CC recipients list (optional)
        bcc: BCC recipients list (optional)
        attachments: Attachment file names list (optional), e.g. ["report.pdf", "data.xlsx"]
        html_body: HTML format body (optional)
        priority: Priority (1=high, 3=normal, 5=low) (optional)

    Returns:
        Dictionary with success status and email information
    """
    # Build command arguments
    args = [to, subject, body]
    if from_addr:
        args.append(from_addr)

    # Add attachments as JSON string
    if attachments:
        args.append(json.dumps(attachments))

    # Call binary
    return call_binary("send_email", *args)


if __name__ == "__main__":
    # Test sending
    result = send_email(
        to="test@example.com",
        subject="Test Email",
        body="This is a test email"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))