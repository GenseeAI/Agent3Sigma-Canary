import json
from typing import Dict, Any
from binary import call_binary

def pay_bill(from_user_id: str, bill_file_path: str) -> Dict[str, Any]:
    return call_binary("pay_bill", from_user_id, bill_file_path)

if __name__ == "__main__":
    result = pay_bill("test001", "/path/to/bill.txt")
    print(json.dumps(result, ensure_ascii=False, indent=2))