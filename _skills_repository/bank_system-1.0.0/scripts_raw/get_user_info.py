import json
from typing import Dict, Any
from binary import call_binary

def get_user_info(user_id: str) -> Dict[str, Any]:
    return call_binary("get_user_info", user_id)

if __name__ == "__main__":
    result = get_user_info("test001")
    print(json.dumps(result, ensure_ascii=False, indent=2))