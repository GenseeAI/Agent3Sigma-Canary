import json
from typing import Optional, Dict, Any
from binary import call_binary

def get_contacts(limit: int = 50, search: str = None) -> Dict[str, Any]:
    args = [str(limit)]
    if search: args.append(search)
    return call_binary("get_contacts", *args)

if __name__ == "__main__":
    result = get_contacts(20)
    print(json.dumps(result, ensure_ascii=False, indent=2))