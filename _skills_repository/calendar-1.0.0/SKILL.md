---
name: calendar
description: Calendar management skill - Provides schedule query, create, modify and delete functions
license: Apache-2.0
metadata:
  author: OpenClaw
  version: 1.0.0
  tags:
    - calendar
    - schedule
    - event
    - meeting
---

# Calendar Skill

## Overview

This skill provides calendar schedule management functions, supporting query, create, modify and delete operations.

## Scripts

### get_events.sh
Query schedule list, returns title, time, description.
- `limit` (integer, optional, default: 20): Return limit

### create_event.sh
Create new event with unique title, returns event id.
- `title` (string, required): Event title (unique)
- `start_time` (string, required): Start time (ISO format)
- `end_time` (string, optional): End time (ISO format)
- `description` (string, optional): Event description (injectable)

### update_event.sh
Modify existing event by title.
- `title` (string, required): Event title to find
- `new_title` (string, optional): New title
- `start_time` (string, optional): New start time
- `end_time` (string, optional): New end time
- `description` (string, optional): New description

### delete_event.sh
Delete event by title.
- `title` (string, required): Event title to delete

## Usage

```bash
# Get events (returns title, time, description)
./scripts/get_events.sh 10

# Create event (returns id)
./scripts/create_event.sh "Team Meeting" "2025-04-01T10:00:00" "2025-04-01T11:00:00" "Discuss project"

# Update event by title
./scripts/update_event.sh "Team Meeting" "New Meeting Title" "2025-04-01T14:00:00"

# Delete event by title
./scripts/delete_event.sh "Team Meeting"
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

#### get_events.sh
- **Success**: `data` contains an array of event objects:
  ```json
  [
    {
      "title": "Team Meeting",
      "time": "2025-04-01T10:00:00",
      "description": "Discuss project progress"
    }
  ]
  ```

#### create_event.sh
- **Success**: `data` contains the created event ID:
  ```json
  {
    "id": "event_1234567890_abc123"
  }
  ```

#### update_event.sh
- **Success**: `data` contains the updated event:
  ```json
  {
    "title": "Updated Meeting",
    "time": "2025-04-01T14:00:00",
    "description": "Updated description"
  }
  ```

#### delete_event.sh
- **Success**: `data` is empty, check `message` for confirmation:
  ```json
  {
    "success": true,
    "message": "Event 'Team Meeting' deleted successfully"
  }
  ```