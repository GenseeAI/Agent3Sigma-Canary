import json
from typing import Optional, List, Dict, Any
from binary import call_binary

def post_tweet(content: str, tags: List[str] = None, reply_to: str = None, media: List[str] = None) -> Dict[str, Any]:
    args = [content]
    if tags:
        args.append(",".join(tags))
    return call_binary("post_tweet", *args)

if __name__ == "__main__":
    result = post_tweet("Hello World!", ["#test"])
    print(json.dumps(result, ensure_ascii=False, indent=2))