import json
from typing import Optional, Dict, Any
from binary import call_binary

def add_contact(user_id: str, nickname: str = None, remark: str = None) -> Dict[str, Any]:
    args = [user_id]
    if nickname: args.append(nickname)
    return call_binary("add_contact", *args)

if __name__ == "__main__":
    result = add_contact("test_user", "Test User")
    print(json.dumps(result, ensure_ascii=False, indent=2))