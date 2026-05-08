import json
from typing import Dict, Any
from binary import call_binary

def get_transfer_records(user_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    return call_binary("get_transfer_records", user_id, str(limit), str(offset))

if __name__ == "__main__":
    result = get_transfer_records("zhangsan", 20, 0)
    print(json.dumps(result, ensure_ascii=False, indent=2))