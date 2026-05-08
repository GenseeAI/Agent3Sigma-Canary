import json
from typing import Dict, Any
from binary import call_binary

def search_tweets(query: str, limit: int = 20) -> Dict[str, Any]:
    return call_binary("search_tweets", query, str(limit))

if __name__ == "__main__":
    result = search_tweets("test")
    print(json.dumps(result, ensure_ascii=False, indent=2))