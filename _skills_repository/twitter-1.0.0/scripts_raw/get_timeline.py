import json
from typing import Dict, Any
from binary import call_binary

def get_timeline(limit: int = 20, username: str = None) -> Dict[str, Any]:
    args = [str(limit)]
    if username:
        args.append(username)
    return call_binary("get_timeline", *args)

if __name__ == "__main__":
    result = get_timeline(10)
    print(json.dumps(result, ensure_ascii=False, indent=2))