
import json, time
from config import API_ID, API_HASH

db = {}
temp = {}
rates = {"BD": 0.2, "IN": 0.15, "ID": 0.1}
timeout = 300

def save_temp(uid, value, phone=False):
    if phone:
        temp[str(uid) + "_phone"] = value
    else:
        temp[uid] = value

def get_temp(uid, phone=False):
    return temp.get(str(uid) + "_phone") if phone else temp.get(uid)

def clear_temp(uid):
    temp.pop(uid, None)
    temp.pop(str(uid) + "_phone", None)

def add_balance(uid, amount):
    uid = str(uid)
    db.setdefault(uid, {"balance": 0, "success": 0, "joined": time.ctime()})
    db[uid]["balance"] += amount

def increment_success(uid):
    uid = str(uid)
    db.setdefault(uid, {"balance": 0, "success": 0, "joined": time.ctime()})
    db[uid]["success"] += 1

def get_user_info(uid):
    uid = str(uid)
    return db.get(uid, {"balance": 0, "success": 0, "joined": time.ctime()})

def reset_balance(uid):
    uid = str(uid)
    db[uid]["balance"] = 0

def get_country_from_phone(phone):
    if phone.startswith("+880"): return "BD"
    if phone.startswith("+91"): return "IN"
    if phone.startswith("+62"): return "ID"
    return "UNKNOWN"

def get_rate(country):
    return rates.get(country.upper(), 0.1)

def set_rate(country, rate):
    rates[country.upper()] = rate

def set_session_timeout(seconds):
    global timeout
    timeout = seconds
