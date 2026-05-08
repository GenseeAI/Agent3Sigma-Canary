import json
from typing import Dict, Any
from binary import call_binary

def login(user_id: str, password: str) -> Dict[str, Any]:
    return call_binary("login", user_id, password)

if __name__ == "__main__":
    result = login("test001", "password123")
    print(json.dumps(result, ensure_ascii=False, indent=2))