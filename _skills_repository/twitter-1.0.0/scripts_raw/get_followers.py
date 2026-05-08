import json
from typing import Dict, Any
from binary import call_binary

def get_followers(limit: int = 50) -> Dict[str, Any]:
    return call_binary("get_followers", str(limit))

if __name__ == "__main__":
    result = get_followers(10)
    print(json.dumps(result, ensure_ascii=False, indent=2))