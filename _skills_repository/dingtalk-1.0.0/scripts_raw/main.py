#!/usr/bin/env python3
"""DingTalk skill binary - standalone executable"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Configuration - hardcoded for binary distribution
DATA_DIR = Path("/tmp/scry/skill_data/dingtalk/data")
CONTACTS_FILE = DATA_DIR / "contacts.json"
MESSAGES_FILE = DATA_DIR / "messages.json"

def load_json(file_path: Path) -> Any:
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] if "contacts" in str(file_path) else {}

def save_json(file_path: Path, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_contacts(limit: int = 50, search: str = None) -> Dict[str, Any]:
    contacts = load_json(CONTACTS_FILE)
    if search:
        contacts = [c for c in contacts if search.lower() in c.get("name", "").lower() or search.lower() in c.get("user_id", "").lower()]
    if limit > 0 and len(contacts) > limit:
        contacts = contacts[:limit]
    return {"success": True, "data": contacts, "message": "Contacts retrieved successfully"}

def add_contact(user_id: str, nickname: str = None, remark: str = None) -> Dict[str, Any]:
    contacts = load_json(CONTACTS_FILE)
    contact = {
        "id": f"contact_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "nickname": nickname or user_id,
        "remark": remark or "",
        "added_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    contacts.append(contact)
    save_json(CONTACTS_FILE, contacts)
    return {"success": True, "data": contact, "message": "Contact added successfully"}

def delete_contact(contact_id: str) -> Dict[str, Any]:
    contacts = load_json(CONTACTS_FILE)
    for i, c in enumerate(contacts):
        if c.get("id") == contact_id:
            del contacts[i]
            save_json(CONTACTS_FILE, contacts)
            return {"success": True, "message": "Contact deleted successfully"}
    return {"success": False, "error": "Contact not found", "message": "Failed to delete contact"}

def get_messages(contact_id: str, limit: int = 20) -> Dict[str, Any]:
    messages = load_json(MESSAGES_FILE)
    messages = [m for m in messages if m.get("contact_id") == contact_id]
    if limit > 0 and len(messages) > limit:
        messages = messages[:limit]
    return {"success": True, "data": messages, "message": "Messages retrieved successfully"}

def send_message(contact_id: str, content: str, message_type: str = "text") -> Dict[str, Any]:
    messages = load_json(MESSAGES_FILE)
    message = {
        "id": f"msg_{uuid.uuid4().hex[:8]}",
        "contact_id": contact_id,
        "content": content,
        "type": message_type,
        "direction": "sent",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "read": True
    }
    messages.insert(0, message)
    save_json(MESSAGES_FILE, messages)
    return {"success": True, "data": message, "message": "Message sent successfully"}

def delete_message(message_id: str) -> Dict[str, Any]:
    messages = load_json(MESSAGES_FILE)
    for i, m in enumerate(messages):
        if m.get("id") == message_id:
            del messages[i]
            save_json(MESSAGES_FILE, messages)
            return {"success": True, "message": "Message deleted successfully"}
    return {"success": False, "error": "Message not found", "message": "Failed to delete message"}

def search_messages(keyword: str, limit: int = 20) -> Dict[str, Any]:
    messages = load_json(MESSAGES_FILE)
    results = [m for m in messages if keyword.lower() in m.get("content", "").lower()]
    if limit > 0 and len(results) > limit:
        results = results[:limit]
    return {"success": True, "data": results, "message": "Search results retrieved successfully"}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command specified", "message": "Usage: dingtalk-1.0.0 <command> [args...]"}))
        sys.exit(1)
    command = sys.argv[1]
    result = None
    try:
        if command == "get_contacts":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            search = sys.argv[3] if len(sys.argv) > 3 else None
            result = get_contacts(limit, search)
        elif command == "add_contact":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing user_id", "message": "Usage: add_contact <user_id> [nickname]"}))
                sys.exit(1)
            result = add_contact(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        elif command == "delete_contact":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing contact_id", "message": "Usage: delete_contact <contact_id>"}))
                sys.exit(1)
            result = delete_contact(sys.argv[2])
        elif command == "get_messages":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing contact_id", "message": "Usage: get_messages <contact_id> [limit]"}))
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = get_messages(sys.argv[2], limit)
        elif command == "send_message":
            if len(sys.argv) < 4:
                print(json.dumps({"success": False, "error": "Missing parameters", "message": "Usage: send_message <contact_id> <content>"}))
                sys.exit(1)
            result = send_message(sys.argv[2], sys.argv[3])
        elif command == "delete_message":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing message_id", "message": "Usage: delete_message <message_id>"}))
                sys.exit(1)
            result = delete_message(sys.argv[2])
        elif command == "search_messages":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing keyword", "message": "Usage: search_messages <keyword> [limit]"}))
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = search_messages(sys.argv[2], limit)
        else:
            result = {"success": False, "error": "Unknown command", "message": f"Command '{command}' not supported"}
    except Exception as e:
        result = {"success": False, "error": str(e), "message": "Operation failed"}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()