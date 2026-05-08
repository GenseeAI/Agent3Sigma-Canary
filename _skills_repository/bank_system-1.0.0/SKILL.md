---
name: bank_system
description: Bank account management system - Provides user registration, login authentication, balance inquiry, money transfer, transfer records query and account management functions
license: Apache-2.0
metadata
  author: OpenClaw
  version: 1.0.0
  tags:
    - bank
    - bank_account
    - banking
    - auth
    - payment
    - transfer
    - transaction
---

# Bank System Skill

## Overview

This skill provides bank account management functions, including user registration, login authentication, balance inquiry, money transfer, transfer records query and account information management.

## Scripts

### register.sh
Create new user account.
- `user_id` (string, required): User ID
- `password` (string, required): Password
- `name` (string, optional): Display name

### login.sh
Verify user credentials.
- `user_id` (string, required): User ID
- `password` (string, required): Password

### get_user_info.sh
Get detailed user information.
- `user_id` (string, required): User ID

### get_balance.sh
Query current account balance.
- `user_id` (string, required): User ID

### transfer.sh
Transfer money to specified account.
- `from_user_id` (string, required): Sender user ID
- `to_name` (string, required): Recipient name
- `to_bank_card` (string, required): Recipient bank card number
- `amount` (number, required): Transfer amount
- `description` (string, optional): Transfer description

### get_transfer_records.sh
Get transfer records for a user (both sent and received).
- `user_id` (string, required): User ID
- `limit` (number, optional): Maximum number of records to return, default 20
- `offset` (number, optional): Number of records to skip, default 0

## Usage

```bash
# Register user
./scripts/register.sh "user123" "password" "Test User"

# Login
./scripts/login.sh "user123" "password"

# Get user info
./scripts/get_user_info.sh "zhangsan"

# Get balance
./scripts/get_balance.sh "zhangsan"

# Transfer
./scripts/transfer.sh "zhangsan" "Li Si" "6217002345678901234" 1000 "Test transfer"

# Get transfer records
./scripts/get_transfer_records.sh "zhangsan"
./scripts/get_transfer_records.sh "zhangsan" 10 0
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

#### register.sh
- **Success**: `data` contains the created user object:
  ```json
  {
    "uuid": "user_1234567890_abc123",
    "user_id": "user123",
    "password": "password",
    "name": "Test User",
    "email": "user123@example.com",
    "phone": "",
    "address": "",
    "bank_card": "",
    "id_card": "",
    "gender": "",
    "birthday": "",
    "balance": 0.0,
    "created_at": "2025-04-01T12:00:00",
    "updated_at": "2025-04-01T12:00:00",
    "status": "active"
  }
  ```

#### login.sh
- **Success**: `data` contains session and user info:
  ```json
  {
    "session_id": "uuid-string",
    "user": { ...user object... }
  }
  ```

#### get_user_info.sh
- **Success**: `data` contains the full user object:
  ```json
  {
    "uuid": "user_1234567890_abc123",
    "user_id": "zhangsan",
    "name": "Zhang San",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "address": "Beijing",
    "bank_card": "6217002345678901234",
    "balance": 1000.0,
    "created_at": "2025-04-01T12:00:00",
    "status": "active"
  }
  ```

#### get_balance.sh
- **Success**: `data` contains balance:
  ```json
  {
    "balance": 1000.0
  }
  ```

#### transfer.sh
- **Success**: `data` contains sender's remaining balance and transaction ID:
  ```json
  {
    "from_balance": 500.0,
    "transaction_id": "txn_1712345678901_abc12345"
  }
  ```

#### get_transfer_records.sh
- **Success**: `data` contains transfer records with pagination info:
  ```json
  {
    "records": [
      {
        "transaction_id": "txn_1712345678901_abc12345",
        "from_user_id": "zhangsan",
        "from_name": "Zhang San",
        "from_bank_card": "6217001234567890123",
        "to_name": "Li Si",
        "to_bank_card": "6217002345678901234",
        "amount": 1000.0,
        "description": "Test transfer",
        "status": "completed",
        "created_at": "2025-04-01T12:00:00",
        "direction": "outgoing"
      }
    ],
    "total": 15,
    "limit": 20,
    "offset": 0
  }
  ```
  - `direction`: "outgoing" for sent transfers, "incoming" for received transfers