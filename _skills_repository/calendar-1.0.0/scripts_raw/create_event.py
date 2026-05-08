import json
from typing import Optional, List, Dict, Any
from binary import call_binary

def create_event(title: str, start_time: str, end_time: str = None, description: str = None, location: str = None, attendees: List[str] = None) -> Dict[str, Any]:
    args = [title, start_time]
    if end_time: args.append(end_time)
    return call_binary("create_event", *args)

if __name__ == "__main__":
    result = create_event("Team Meeting", "2025-04-01T10:00:00", "2025-04-01T11:00:00")
    print(json.dumps(result, ensure_ascii=False, indent=2))