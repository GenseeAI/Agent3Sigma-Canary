---
name: dingtalk
description: DingTalk skill - Provides contact management, message sending and receiving functions for DingTalk
license: Apache-2.0
metadata:
  author: OpenClaw
  version: 1.0.0
  tags:
    - dingtalk
    - im
    - messaging
    - chat
    - communication
---

# DingTalk Skill

## Overview

This skill provides DingTalk instant messaging functions, supporting contact management, message sending and receiving operations.

## Scripts

### get_contacts.sh
Get all contacts with optional search filter.
- `limit` (integer, optional, default: 50): Return limit
- `search` (string, optional): Search keyword

### add_contact.sh
Add new contact with optional nickname.
- `user_id` (string, required): User ID
- `nickname` (string, optional): Nickname

### delete_contact.sh
Delete specified contact.
- `contact_id` (string, required): Contact ID

### get_messages.sh
Get chat history with specified contact.
- `contact_id` (string, required): Contact ID
- `limit` (integer, optional, default: 20): Return limit

### send_message.sh
Send message to contact.
- `contact_id` (string, required): Contact ID
- `content` (string, required): Message content

### delete_message.sh
Delete specified message.
- `message_id` (string, required): Message ID

### search_messages.sh
Keyword search message history.
- `keyword` (string, required): Search keyword
- `limit` (integer, optional, default: 20): Return limit

## Usage

```bash
# Get contacts
./scripts/get_contacts.sh 20

# Add contact
./scripts/add_contact.sh "user123" "Nickname"

# Delete contact
./scripts/delete_contact.sh "contact_xxx"

# Get messages
./scripts/get_messages.sh "contact_xxx" 20

# Send message
./scripts/send_message.sh "contact_xxx" "Hello!"

# Delete message
./scripts/delete_message.sh "msg_xxx"

# Search messages
./scripts/search_messages.sh "hello" 10
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

#### get_contacts.sh
- **Success**: `data` contains an array of contact objects:
  ```json
  [
    {
      "id": "contact_abc123",
      "user_id": "user123",
      "nickname": "John",
      "remark": "",
      "added_at": "2025-04-01T12:00:00"
    }
  ]
  ```

#### add_contact.sh
- **Success**: `data` contains the added contact object:
  ```json
  {
    "id": "contact_abc123",
    "user_id": "user123",
    "nickname": "John",
    "remark": "",
    "added_at": "2025-04-01T12:00:00"
  }
  ```

#### delete_contact.sh
- **Success**: `data` is empty, check `message` for confirmation:
  ```json
  {
    "success": true,
    "message": "Contact deleted successfully"
  }
  ```

#### get_messages.sh
- **Success**: `data` contains an array of message objects:
  ```json
  [
    {
      "id": "msg_abc123",
      "contact_id": "contact_abc123",
      "content": "Hello!",
      "type": "text",
      "direction": "sent",
      "timestamp": "2025-04-01T12:00:00",
      "read": true
    }
  ]
  ```

#### send_message.sh
- **Success**: `data` contains the sent message object:
  ```json
  {
    "id": "msg_abc123",
    "contact_id": "contact_abc123",
    "content": "Hello!",
    "type": "text",
    "direction": "sent",
    "timestamp": "2025-04-01T12:00:00",
    "read": true
  }
  ```

#### delete_message.sh
- **Success**: `data` is empty, check `message` for confirmation:
  ```json
  {
    "success": true,
    "message": "Message deleted successfully"
  }
  ```

#### search_messages.sh
- **Success**: `data` contains an array of matching message objects:
  ```json
  [
    {
      "id": "msg_abc123",
      "contact_id": "contact_abc123",
      "content": "Hello world!",
      "type": "text",
      "direction": "sent",
      "timestamp": "2025-04-01T12:00:00",
      "read": true
    }
  ]
  ```