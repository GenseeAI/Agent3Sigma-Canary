---
name: twitter
description: Twitter skill - Provides posting, timeline viewing, follower management and other functions
license: Apache-2.0
metadata:
  author: OpenClaw
  version: 1.0.0
  tags:
    - twitter
    - social
    - social-media
---

# Twitter Skill

## Overview

This skill provides Twitter social media functionality, including viewing followers, posting tweets, browsing timeline and more.

## Scripts

### post_tweet.sh
Post a new tweet with optional hashtags.
- `content` (string, required): Tweet content
- `tags` (array, optional): Hashtag list
- `reply_to` (string, optional): Reply to tweet ID

### get_timeline.sh
Get user timeline with pagination.
- `limit` (integer, optional, default: 20): Number of tweets to return
- `username` (string, optional): Filter by username

### get_followers.sh
Get user followers list.
- `limit` (integer, optional, default: 50): Number of followers to return

### get_following.sh
Get user following list.
- `limit` (integer, optional, default: 50): Number of following to return

### search_tweets.sh
Keyword search tweets.
- `query` (string, required): Search keyword
- `limit` (integer, optional, default: 20): Number of results to return

### get_comments.sh
Get comments list for a post (feedback on a topic).
- `post_id` (string, required): Post ID to get comments for
- `limit` (integer, optional, default: 20): Number of comments to return

## Usage

```bash
# Post tweet
./scripts/post_tweet.sh "Hello World!" "#python,#coding"

# Get timeline
./scripts/get_timeline.sh 20

# Get followers
./scripts/get_followers.sh 50

# Get following
./scripts/get_following.sh 50

# Search tweets
./scripts/search_tweets.sh "python" 10

# Get comments for a post
./scripts/get_comments.sh "post_xxx" 20
```

## Return Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message",
  "message": "Operation failed"
}
```

### Script-specific Response Data

#### post_tweet.sh
- **Success**: `data` contains the posted tweet object:
  ```json
  {
    "id": "post_1234567890_abc123",
    "username": "openclaw",
    "handle": "@openclaw",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=openclaw",
    "content": "Hello World!",
    "tags": ["python", "coding"],
    "reply_to": null,
    "media": [],
    "timestamp": "2025-04-01T12:00:00Z",
    "likes": 0,
    "retweets": 0,
    "replies": 0,
    "views": 0
  }
  ```

#### get_timeline.sh
- **Success**: `data` contains an array of tweet objects:
  ```json
  [
    {
      "id": "post_1234567890_abc123",
      "username": "openclaw",
      "handle": "@openclaw",
      "content": "Hello World!",
      "tags": ["python"],
      "timestamp": "2025-04-01T12:00:00Z",
      "likes": 5,
      "retweets": 2,
      "replies": 1,
      "views": 100
    }
  ]
  ```

#### get_followers.sh
- **Success**: `data` contains an array of follower objects:
  ```json
  [
    {
      "id": "user_abc123",
      "username": "follower1",
      "handle": "@follower1",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=follower1",
      "bio": "Follower bio"
    }
  ]
  ```

#### get_following.sh
- **Success**: `data` contains an array of following user objects:
  ```json
  [
    {
      "id": "user_def456",
      "username": "following1",
      "handle": "@following1",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=following1",
      "bio": "Following user bio"
    }
  ]
  ```

#### search_tweets.sh
- **Success**: `data` contains an array of matching tweet objects:
  ```json
  [
    {
      "id": "post_1234567890_abc123",
      "username": "openclaw",
      "content": "Python tutorial",
      "tags": ["python", "tutorial"],
      "timestamp": "2025-04-01T12:00:00Z",
      "likes": 10,
      "retweets": 5
    }
  ]
  ```

#### get_comments.sh
- **Success**: `data` contains an array of comment objects for the specified post:
  ```json
  [
    {
      "id": "comment_abc123",
      "post_id": "post_1234567890_abc123",
      "username": "user1",
      "content": "Great post!",
      "timestamp": "2025-04-01T12:30:00Z"
    }
  ]
  ```