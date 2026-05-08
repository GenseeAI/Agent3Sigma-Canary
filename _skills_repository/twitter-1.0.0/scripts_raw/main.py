#!/usr/bin/env python3
"""Twitter skill binary - standalone executable"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Configuration - hardcoded for binary distribution
DATA_DIR = Path("/tmp/scry/skill_data/twitter/data")
DEFAULT_USERNAME = "openclaw"
DEFAULT_HANDLE = "@openclaw"
POSTS_FILE = DATA_DIR / "posts.json"
TIMELINE_FILE = DATA_DIR / "timeline.json"
COMMENTS_FILE = DATA_DIR / "comments.json"

def load_json(file_path: Path) -> List[Dict]:
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(file_path: Path, data: List[Dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def post_tweet(content: str, tags: List[str] = None, reply_to: str = None) -> Dict[str, Any]:
    post = {
        "id": f"post_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        "username": DEFAULT_USERNAME,
        "handle": DEFAULT_HANDLE,
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={DEFAULT_USERNAME}",
        "content": content,
        "tags": tags or [],
        "reply_to": reply_to,
        "media": [],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "likes": 0, "retweets": 0, "replies": 0, "views": 0
    }
    posts = load_json(POSTS_FILE)
    posts.insert(0, post)
    save_json(POSTS_FILE, posts)
    timeline = load_json(TIMELINE_FILE)
    timeline.insert(0, post)
    save_json(TIMELINE_FILE, timeline)
    return {"success": True, "data": post, "message": "Tweet posted successfully"}

def get_timeline(limit: int = 20, username: str = None) -> Dict[str, Any]:
    timeline = load_json(TIMELINE_FILE)
    if username:
        timeline = [p for p in timeline if p.get("username") == username]
    if limit > 0 and len(timeline) > limit:
        timeline = timeline[:limit]
    return {"success": True, "data": timeline, "message": "Timeline retrieved successfully"}

def get_followers(limit: int = 50) -> Dict[str, Any]:
    followers_file = DATA_DIR / "followers.json"
    followers = load_json(followers_file)
    if limit > 0 and len(followers) > limit:
        followers = followers[:limit]
    return {"success": True, "data": followers, "message": "Followers retrieved successfully"}

def get_following(limit: int = 50) -> Dict[str, Any]:
    following_file = DATA_DIR / "following.json"
    following = load_json(following_file)
    if limit > 0 and len(following) > limit:
        following = following[:limit]
    return {"success": True, "data": following, "message": "Following retrieved successfully"}

def search_tweets(query: str, limit: int = 20) -> Dict[str, Any]:
    posts = load_json(POSTS_FILE)
    results = [p for p in posts if query.lower() in p.get("content", "").lower() or any(query.lower() in t.lower() for t in p.get("tags", []))]
    if limit > 0 and len(results) > limit:
        results = results[:limit]
    return {"success": True, "data": results, "message": "Search results retrieved successfully"}

def get_comments(post_id: str, limit: int = 20) -> Dict[str, Any]:
    """Get the comment list for a post."""
    comments = load_json(COMMENTS_FILE)
    # Filter comments for the specified post
    results = [c for c in comments if c.get("post_id") == post_id]
    if limit > 0 and len(results) > limit:
        results = results[:limit]
    return {"success": True, "data": results, "message": "Comments retrieved successfully"}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command specified", "message": "Usage: twitter-1.0.0 <command> [args...]"}))
        sys.exit(1)
    command = sys.argv[1]
    result = None
    try:
        if command == "post_tweet":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing content", "message": "Usage: post_tweet <content> [tags...]"}))
                sys.exit(1)
            result = post_tweet(sys.argv[2], sys.argv[3].split(",") if len(sys.argv) > 3 else None)
        elif command == "get_timeline":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            username = sys.argv[3] if len(sys.argv) > 3 else None
            result = get_timeline(limit, username)
        elif command == "get_followers":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            result = get_followers(limit)
        elif command == "get_following":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            result = get_following(limit)
        elif command == "search_tweets":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing query", "message": "Usage: search_tweets <query> [limit]"}))
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = search_tweets(sys.argv[2], limit)
        elif command == "get_comments":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing post_id", "message": "Usage: get_comments <post_id> [limit]"}))
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = get_comments(sys.argv[2], limit)
        else:
            result = {"success": False, "error": "Unknown command", "message": f"Command '{command}' not supported"}
    except Exception as e:
        result = {"success": False, "error": str(e), "message": "Operation failed"}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
