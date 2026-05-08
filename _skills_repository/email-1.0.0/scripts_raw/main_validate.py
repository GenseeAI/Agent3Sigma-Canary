#!/usr/bin/env python3
"""
Email skill binary - standalone executable
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Configuration - hardcoded for binary distribution
DATA_DIR = Path("/tmp/scry/skill_data/email/data")
DEFAULT_FROM = "openclaw@example.com"
SENT_FILE = DATA_DIR / "sent.json"
INBOX_FILE = DATA_DIR / "inbox.json"
DRAFTS_FILE = DATA_DIR / "drafts.json"
ATTACHMENTS_DIR = DATA_DIR / "attachments"


def load_json(file_path: Path) -> List[Dict]:
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_json(file_path: Path, data: List[Dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_email(to: str, subject: str, body: str, from_addr: str = None, attachments: List[str] = None) -> Dict[str, Any]:
    if not to:
        return {"success": False, "error": "Recipient cannot be empty", "message": "Please provide recipient"}
    if not subject:
        return {"success": False, "error": "Subject cannot be empty", "message": "Please provide subject"}

    from_addr = from_addr or DEFAULT_FROM
    email_id = f"email_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Process attachments - check file existence and get real size
    attachment_objects = []
    if attachments:
        for filename in attachments:
            # Check in attachments directory
            file_path = ATTACHMENTS_DIR / filename
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Attachment not found: {filename}",
                    "message": f"File '{filename}' does not exist in attachments directory"
                }

            # Get real file size
            file_size = file_path.stat().st_size
            attachment_objects.append({
                "name": filename,
                "size": file_size
            })

    email = {
        "id": email_id,
        "from": from_addr,
        "to": to,
        "subject": subject,
        "body": body,
        "cc": [],
        "attachments": attachment_objects,
        "timestamp": timestamp,
        "folder": "sent",
        "read": True
    }

    sent_emails = load_json(SENT_FILE)
    sent_emails.insert(0, email)
    save_json(SENT_FILE, sent_emails)

    return {"success": True, "data": email, "message": f"Email sent to {to}"}


def receive_email(limit: int = 10, folder: str = "inbox") -> Dict[str, Any]:
    if folder == "inbox":
        emails = load_json(INBOX_FILE)
    elif folder == "sent":
        emails = load_json(SENT_FILE)
    elif folder == "drafts":
        emails = load_json(DRAFTS_FILE)
    else:
        emails = load_json(INBOX_FILE)

    if limit > 0 and len(emails) > limit:
        emails = emails[:limit]

    # Remove body field from each email for list view
    emails_without_body = []
    for email in emails:
        email_copy = {k: v for k, v in email.items() if k != "body"}
        emails_without_body.append(email_copy)

    return {"success": True, "data": emails_without_body, "message": "Emails retrieved successfully"}


def read_email(email_id: str) -> str:
    all_emails = load_json(INBOX_FILE) + load_json(SENT_FILE) + load_json(DRAFTS_FILE)
    for email in all_emails:
        if email.get("id") == email_id:
            return email.get("body", "")
    return ""


def delete_email(email_id: str) -> Dict[str, Any]:
    inbox = load_json(INBOX_FILE)
    for i, email in enumerate(inbox):
        if email.get("id") == email_id:
            del inbox[i]
            save_json(INBOX_FILE, inbox)
            return {"success": True, "message": "Email deleted successfully"}

    sent = load_json(SENT_FILE)
    for i, email in enumerate(sent):
        if email.get("id") == email_id:
            del sent[i]
            save_json(SENT_FILE, sent)
            return {"success": True, "message": "Email deleted successfully"}

    return {"success": False, "error": "Email not found", "message": "Failed to delete email"}


def get_attachments(email_id: str) -> Dict[str, Any]:
    all_emails = load_json(INBOX_FILE) + load_json(SENT_FILE) + load_json(DRAFTS_FILE)
    for email in all_emails:
        if email.get("id") == email_id:
            return {"success": True, "data": [], "message": "Attachments retrieved successfully"}
    return {"success": False, "error": "Email not found", "message": "Failed to get attachments"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command specified", "message": "Usage: py_bin_email-1.0.0 <command> [args...]"}))
        sys.exit(1)

    command = sys.argv[1]
    result = None

    try:
        if command == "send_email":
            if len(sys.argv) < 5:
                print(json.dumps({"success": False, "error": "Missing required parameters", "message": "Usage: send_email <to> <subject> <body> [from] [attachments_json]"}))
                sys.exit(1)
            from_addr = sys.argv[5] if len(sys.argv) > 5 else None
            attachments = None
            if len(sys.argv) > 6:
                try:
                    attachments = json.loads(sys.argv[6])
                except json.JSONDecodeError:
                    attachments = None
            result = send_email(sys.argv[2], sys.argv[3], sys.argv[4], from_addr, attachments)

        elif command == "receive_email":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            folder = sys.argv[3] if len(sys.argv) > 3 else "inbox"
            result = receive_email(limit, folder)

        elif command == "read_email":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing email_id", "message": "Usage: read_email <email_id>"}))
                sys.exit(1)
            # read_email returns string directly (body content)
            print(read_email(sys.argv[2]))
            sys.exit(0)

        elif command == "delete_email":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing email_id", "message": "Usage: delete_email <email_id>"}))
                sys.exit(1)
            result = delete_email(sys.argv[2])

        elif command == "get_attachments":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing email_id", "message": "Usage: get_attachments <email_id>"}))
                sys.exit(1)
            result = get_attachments(sys.argv[2])

        else:
            result = {"success": False, "error": "Unknown command", "message": f"Command '{command}' not supported"}

    except Exception as e:
        result = {"success": False, "error": str(e), "message": "Operation failed"}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()