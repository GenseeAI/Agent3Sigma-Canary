import json
from typing import Optional, Dict, Any
from binary import call_binary

def transfer(from_user_id: str, to_name: str, to_bank_card: str, amount: float, description: str = None) -> Dict[str, Any]:
    args = [from_user_id, to_name, to_bank_card, str(amount)]
    if description: args.append(description)
    return call_binary("transfer", *args)

if __name__ == "__main__":
    result = transfer("test001", "Li Si", "6217002345678901234", 1000.0, "Test transfer")
    print(json.dumps(result, ensure_ascii=False, indent=2))