import json
from typing import Optional, Dict, Any
from binary import call_binary

def update_event(event_id: str, title: str = None, start_time: str = None, end_time: str = None, description: str = None, location: str = None) -> Dict[str, Any]:
    args = [event_id]
    if title: args.append(title)
    return call_binary("update_event", *args)

if __name__ == "__main__":
    result = update_event("event_xxx", "New Title")
    print(json.dumps(result, ensure_ascii=False, indent=2))