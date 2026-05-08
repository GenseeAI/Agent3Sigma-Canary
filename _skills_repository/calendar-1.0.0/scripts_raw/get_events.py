import json
from typing import Optional, List, Dict, Any
from binary import call_binary

def get_events(limit: int = 20, start_date: str = None, end_date: str = None, event_id: str = None) -> Dict[str, Any]:
    args = [str(limit)]
    if start_date: args.append(start_date)
    if end_date: args.append(end_date)
    if event_id: args.append(event_id)
    return call_binary("get_events", *args)

if __name__ == "__main__":
    result = get_events(10)
    print(json.dumps(result, ensure_ascii=False, indent=2))