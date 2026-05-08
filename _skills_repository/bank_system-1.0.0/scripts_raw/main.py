#!/usr/bin/env python3
"""Bank System skill binary - standalone executable"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
import uuid

# Configuration - hardcoded for binary distribution
DATA_DIR = Path("/tmp/scry/skill_data/bank_system/data")
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

def load_json(file_path: Path) -> Any:
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] if "users" in str(file_path) else {}

def save_json(file_path: Path, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register(user_id: str, password: str, name: str = None, email: str = None, phone: str = None, address: str = None, bank_card: str = None, id_card: str = None) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    for u in users:
        if u.get("user_id") == user_id:
            return {"success": False, "error": "User already exists", "message": "Registration failed"}
    user = {
        "uuid": f"user_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}",
        "user_id": user_id, "password": password,
        "name": name or user_id, "email": email or f"{user_id}@example.com",
        "phone": phone or "", "address": address or "",
        "bank_card": bank_card or "", "id_card": id_card or "",
        "gender": "", "birthday": "",
        "balance": 0.0,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "active"
    }
    users.append(user)
    save_json(USERS_FILE, users)
    return {"success": True, "data": user, "message": "User registered successfully"}

def login(user_id: str, password: str) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    for u in users:
        if u.get("user_id") == user_id and u.get("password") == password:
            session_id = str(uuid.uuid4())
            sessions = load_json(SESSIONS_FILE)
            sessions[session_id] = {"user_id": user_id, "login_time": time.strftime("%Y-%m-%dT%H:%M:%S")}
            save_json(SESSIONS_FILE, sessions)
            return {"success": True, "data": {"session_id": session_id, "user": u}, "message": "Login successful"}
    return {"success": False, "error": "Invalid credentials", "message": "Login failed"}

def get_user_info(user_id: str) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    for u in users:
        if u.get("user_id") == user_id:
            return {"success": True, "data": u, "message": "User info retrieved successfully"}
    return {"success": False, "error": "User not found", "message": "Failed to get user info"}

def get_balance(user_id: str) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    for u in users:
        if u.get("user_id") == user_id:
            return {"success": True, "data": {"balance": u.get("balance", 0.0)}, "message": "Balance retrieved successfully"}
    return {"success": False, "error": "User not found", "message": "Failed to get balance"}

def transfer(from_user_id: str, to_name: str, to_bank_card: str, amount: float, description: str = None) -> Dict[str, Any]:
    users = load_json(USERS_FILE)
    from_user = None
    for u in users:
        if u.get("user_id") == from_user_id:
            from_user = u
            break
    if not from_user:
        return {"success": False, "error": "Sender not found", "message": "Transfer failed"}
    if from_user.get("balance", 0) < amount:
        return {"success": False, "error": "Insufficient balance", "message": "Transfer failed"}
    from_user["balance"] = from_user.get("balance", 0) - amount
    save_json(USERS_FILE, users)

    # Record transaction
    transactions = load_json(TRANSACTIONS_FILE)
    transaction = {
        "transaction_id": f"txn_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        "from_user_id": from_user_id,
        "from_name": from_user.get("name", from_user_id),
        "from_bank_card": from_user.get("bank_card", ""),
        "to_name": to_name,
        "to_bank_card": to_bank_card,
        "amount": amount,
        "description": description or "",
        "status": "completed",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    transactions.append(transaction)
    save_json(TRANSACTIONS_FILE, transactions)

    return {"success": True, "data": {"from_balance": from_user["balance"], "transaction_id": transaction["transaction_id"]}, "message": f"Transferred {amount} to {to_name}"}

def get_transfer_records(user_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """Get transfer records for a user (both sent and received based on bank card matching)"""
    users = load_json(USERS_FILE)
    user = None
    for u in users:
        if u.get("user_id") == user_id:
            user = u
            break
    if not user:
        return {"success": False, "error": "User not found", "message": "Failed to get transfer records"}

    transactions = load_json(TRANSACTIONS_FILE)
    user_bank_card = user.get("bank_card", "")

    # Filter transactions where user is sender or receiver
    user_transactions = []
    for txn in transactions:
        if txn.get("from_user_id") == user_id:
            txn_copy = txn.copy()
            txn_copy["direction"] = "outgoing"
            user_transactions.append(txn_copy)
        elif txn.get("to_bank_card") == user_bank_card and user_bank_card:
            txn_copy = txn.copy()
            txn_copy["direction"] = "incoming"
            user_transactions.append(txn_copy)

    # Sort by created_at descending
    user_transactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Apply pagination
    total = len(user_transactions)
    paginated = user_transactions[offset:offset + limit]

    return {
        "success": True,
        "data": {
            "records": paginated,
            "total": total,
            "limit": limit,
            "offset": offset
        },
        "message": f"Retrieved {len(paginated)} transfer records"
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command specified", "message": "Usage: bank_system-1.0.0 <command> [args...]"}))
        sys.exit(1)
    command = sys.argv[1]
    result = None
    try:
        if command == "register":
            if len(sys.argv) < 4:
                print(json.dumps({"success": False, "error": "Missing parameters", "message": "Usage: register <user_id> <password> [name]"}))
                sys.exit(1)
            result = register(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        elif command == "login":
            if len(sys.argv) < 4:
                print(json.dumps({"success": False, "error": "Missing parameters", "message": "Usage: login <user_id> <password>"}))
                sys.exit(1)
            result = login(sys.argv[2], sys.argv[3])
        elif command == "get_user_info":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing user_id", "message": "Usage: get_user_info <user_id>"}))
                sys.exit(1)
            result = get_user_info(sys.argv[2])
        elif command == "get_balance":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing user_id", "message": "Usage: get_balance <user_id>"}))
                sys.exit(1)
            result = get_balance(sys.argv[2])
        elif command == "transfer":
            if len(sys.argv) < 6:
                print(json.dumps({"success": False, "error": "Missing parameters", "message": "Usage: transfer <from_user_id> <to_name> <to_bank_card> <amount> [description]"}))
                sys.exit(1)
            result = transfer(sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6] if len(sys.argv) > 6 else None)
        elif command == "get_transfer_records":
            if len(sys.argv) < 3:
                print(json.dumps({"success": False, "error": "Missing user_id", "message": "Usage: get_transfer_records <user_id> [limit] [offset]"}))
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            offset = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            result = get_transfer_records(sys.argv[2], limit, offset)
        else:
            result = {"success": False, "error": "Unknown command", "message": f"Command '{command}' not supported"}
    except Exception as e:
        result = {"success": False, "error": str(e), "message": "Operation failed"}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()