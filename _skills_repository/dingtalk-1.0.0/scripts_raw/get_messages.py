import json
from typing import Dict, Any
from binary import call_binary

def get_messages(contact_id: str, limit: int = 20) -> Dict[str, Any]:
    return call_binary("get_messages", contact_id, str(limit))

if __name__ == "__main__":
    result = get_messages("contact_xxx", 10)
    print(json.dumps(result, ensure_ascii=False, indent=2))