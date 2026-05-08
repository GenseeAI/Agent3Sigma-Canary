import json
from typing import Dict, Any
from binary import call_binary

def send_message(contact_id: str, content: str, message_type: str = "text") -> Dict[str, Any]:
    return call_binary("send_message", contact_id, content)

if __name__ == "__main__":
    result = send_message("contact_xxx", "Hello!")
    print(json.dumps(result, ensure_ascii=False, indent=2))