import json
from typing import Dict, Any
from binary import call_binary

def delete_contact(contact_id: str) -> Dict[str, Any]:
    return call_binary("delete_contact", contact_id)

if __name__ == "__main__":
    result = delete_contact("contact_xxx")
    print(json.dumps(result, ensure_ascii=False, indent=2))