import json
from typing import Dict, Any
from binary import call_binary

def search_messages(keyword: str, limit: int = 20) -> Dict[str, Any]:
    return call_binary("search_messages", keyword, str(limit))

if __name__ == "__main__":
    result = search_messages("hello")
    print(json.dumps(result, ensure_ascii=False, indent=2))