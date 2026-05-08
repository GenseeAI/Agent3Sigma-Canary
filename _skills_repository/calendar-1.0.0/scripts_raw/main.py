#!/usr/bin/env python3
"""Calendar skill binary - standalone executable"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Configuration - hardcoded for binary distribution
DATA_DIR = Path("/tmp/scry/skill_data/calendar/data")
DEFAULT_TIMEZONE = "Asia/Shanghai"
EVENTS_FILE = DATA_DIR / "events.json"

def load_json(file_path: Path) -> List[Dict]:
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(file_path: Path, data: List[Dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_events(limit: int = 20) -> Dict[str, Any]:
    """Query events and return title, time, and description."""
    events = load_json(EVENTS_FILE)
    result = []
    for e in events[:limit]:
        result.append({
            "title": e.get("title", ""),
            "time": e.get("start_time", ""),
            "description": e.get("description", "")
        })
    return {"success": True, "data": result, "message": "Events retrieved successfully"}

def create_event(title: str, start_time: str, end_time: str = None, description: str = None) -> Dict[str, Any]:
    """Create an event and return its id. Duplicate names are not allowed."""
    events = load_json(EVENTS_FILE)

    # Check whether an event with the same title already exists
    for e in events:
        if e.get("title") == title:
            return {"success": False, "error": f"Event with title '{title}' already exists", "message": "Failed to create event"}

    event_id = f"event_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
    event = {
        "id": event_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time or start_time,
        "description": description or "",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    events.insert(0, event)
    save_json(EVENTS_FILE, events)
    return {"success": True, "data": {"id": event_id}, "message": "Event created successfully"}

def update_event(title: str, new_title: str = None, start_time: str = None, end_time: str = None, description: str = None) -> Dict[str, Any]:
    """Update an event by name."""
    events = load_json(EVENTS_FILE)
    for i, e in enumerate(events):
        if e.get("title") == title:
            if new_title:
                # Check whether the new title already exists
                for other in events:
                    if other.get("title") == new_title and other.get("id") != e.get("id"):
                        return {"success": False, "error": f"Event with title '{new_title}' already exists", "message": "Failed to update event"}
                e["title"] = new_title
            if start_time:
                e["start_time"] = start_time
            if end_time:
                e["end_time"] = end_time
            if description is not None:
                e["description"] = description
            save_json(EVENTS_FILE, events)
            return {"success": True, "data": {"title": e["title"], "time": e["start_time"], "description": e["description"]}, "message": "Event updated successfully"}
    return {"success": False, "error": f"Event with title '{title}' not found", "message": "Failed to update event"}

def delete_event(title: str) -> Dict[str, Any]:
    """Delete an event by name."""
    events = load_json(EVENTS_FILE)
    for i, e in enumerate(events):
        if e.get("title") == title:
            del events[i]
            save_json(EVENTS_FILE, events)
            return {"success": True, "message": f"Event '{title}' deleted successfully"}
    return {"success": False, "error": f"Event with title '{title}' not found", "message": "Failed to delete event"}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command specified", "message": "Usage: py_bin_calendar-1.0.0 <command> [args...]"}))
        sys.exit(1)
    command = sys.argv[1]
    result = None
    try:
        if command == "get_events":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            result = get_events(limit)
        elif command == "create_event":
            if len(sys.argv) < 4:
                print(json.dumps({"success": False, "error": "Missing parameters", "message": "Usage: create_event <title> <start_time> [end_time] [description]"}))
                sys.exit(1)
            result = create_event(
                sys.argv[2],
                sys.argv[3],
                sys.argv[4] if len(sys.argv) > 4 else None,
                sys.argv[5] if len(sys.argv) > 5 else None
            )
        elif command == "update_event":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing title", "message": "Usage: update_event <title> [new_title] [start_time] [end_time] [description]"}))
                sys.exit(1)
            result = update_event(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else None,
                sys.argv[4] if len(sys.argv) > 4 else None,
                sys.argv[5] if len(sys.argv) > 5 else None,
                sys.argv[6] if len(sys.argv) > 6 else None
            )
        elif command == "delete_event":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing title", "message": "Usage: delete_event <title>"}))
                sys.exit(1)
            result = delete_event(sys.argv[2])
        else:
            result = {"success": False, "error": "Unknown command", "message": f"Command '{command}' not supported"}
    except Exception as e:
        result = {"success": False, "error": str(e), "message": "Operation failed"}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
