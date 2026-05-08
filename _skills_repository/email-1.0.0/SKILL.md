---
name: email
description: Email skill - Provides email sending, receiving, reading and management functions
license: Apache-2.0
metadata:
  author: OpenClaw
  version: 1.0.0
  tags:
    - email
    - mail
    - communication
---

# Email Skill

## Overview

This skill provides email functionality, supporting email sending, receiving, reading and management operations.

## Scripts

### send_email.sh
Send email to specified recipient.
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body content
- `from_addr` (string, optional): Sender email address
- `attachments` (JSON string, optional): Attachment file names list, e.g. '["report.pdf", "data.xlsx"]'

### receive_email.sh
Get email list from specified folder.
- `limit` (integer, optional, default: 10): Number of emails to return
- `folder` (string, optional, default: inbox): Folder name

### read_email.sh
Read single email details by ID.
- `email_id` (string, required): Email ID

### delete_email.sh
Delete specified email by ID.
- `email_id` (string, required): Email ID

### get_attachments.sh
Get email attachment information.
- `email_id` (string, required): Email ID

## Usage

```bash
# Send email
./scripts/send_email.sh "user@example.com" "Subject" "Body"

# Send email with attachment
./scripts/send_email.sh "user@example.com" "Subject" "Body" "sender@example.com" '["report.pdf"]'

# Receive emails
./scripts/receive_email.sh 10 inbox

# Read email
./scripts/read_email.sh "email_xxx"

# Delete email
./scripts/delete_email.sh "email_xxx"

# Get attachments
./scripts/get_attachments.sh "email_xxx"
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

#### send_email.sh
- **Success**: `data` contains the sent email object:
  ```json
  {
    "id": "email_1234567890_abc123",
    "from": "openclaw@example.com",
    "to": "user@example.com",
    "subject": "Subject",
    "body": "Body content",
    "cc": [],
    "attachments": [
      {"name": "report.pdf", "size": 102400}
    ],
    "timestamp": "2025-04-01T12:00:00Z",
    "folder": "sent",
    "read": true
  }
  ```

#### receive_email.sh
- **Success**: `data` contains an array of email objects (without body field):
  ```json
  [
    {
      "id": "email_1234567890_abc123",
      "from": "sender@example.com",
      "to": "openclaw@example.com",
      "subject": "Email Subject",
      "timestamp": "2025-04-01T12:00:00Z",
      "folder": "inbox",
      "read": false
    }
  ]
  ```
  Note: The `body` field is excluded from the list view for efficiency. Use `read_email.sh` to get the full email content including body.

#### read_email.sh
- **Success**: `data` contains the full email object:
  ```json
  {
    "id": "email_1234567890_abc123",
    "from": "sender@example.com",
    "to": "openclaw@example.com",
    "subject": "Email Subject",
    "body": "Email body content",
    "cc": [],
    "timestamp": "2025-04-01T12:00:00Z",
    "folder": "inbox",
    "read": true
  }
  ```

#### delete_email.sh
- **Success**: `data` is empty, check `message` for confirmation:
  ```json
  {
    "success": true,
    "message": "Email deleted successfully"
  }
  ```

#### get_attachments.sh
- **Success**: `data` contains an array of attachments (currently empty array):
  ```json
  []
  ```