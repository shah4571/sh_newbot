import json
from pathlib import Path
from datetime import datetime

db_path = Path("bot/utils/database.json")
db_path.parent.mkdir(parents=True, exist_ok=True)
if not db_path.exists():
    db_path.write_text(json.dumps({"users": {}, "rates": {}, "verify_time": 300}))

def read_db():
    return json.loads(db_path.read_text())

def write_db(data):
    db_path.write_text(json.dumps(data, indent=2))

def register_user(user_id):
    db = read_db()
    if str(user_id) not in db["users"]:
        db["users"][str(user_id)] = {
            "balance": 0.0,
            "success": 0,
            "joined": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        write_db(db)

def update_balance(user_id, amount):
    db = read_db()
    uid = str(user_id)
    db["users"][uid]["balance"] += amount
    db["users"][uid]["success"] += 1
    write_db(db)

def get_user_info(user_id):
    db = read_db()
    return db["users"].get(str(user_id), {})

def set_country_rate(country, rate):
    db = read_db()
    db["rates"][country] = rate
    write_db(db)

def get_country_rates():
    return read_db().get("rates", {})

def set_verify_time(seconds):
    db = read_db()
    db["verify_time"] = seconds
    write_db(db)

def get_verify_time():
    return read_db().get("verify_time", 300)
