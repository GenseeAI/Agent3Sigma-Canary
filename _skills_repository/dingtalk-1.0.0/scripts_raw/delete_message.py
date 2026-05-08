import json
from typing import Dict, Any
from binary import call_binary

def delete_message(message_id: str) -> Dict[str, Any]:
    return call_binary("delete_message", message_id)

if __name__ == "__main__":
    result = delete_message("msg_xxx")
    print(json.dumps(result, ensure_ascii=False, indent=2))