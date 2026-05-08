import json
from typing import Optional, Dict, Any
from binary import call_binary

def register(user_id: str, password: str, name: str = None, email: str = None, phone: str = None, address: str = None, bank_card: str = None, id_card: str = None) -> Dict[str, Any]:
    args = [user_id, password]
    if name: args.append(name)
    return call_binary("register", *args)

if __name__ == "__main__":
    result = register("testuser", "password123", "Test User")
    print(json.dumps(result, ensure_ascii=False, indent=2))