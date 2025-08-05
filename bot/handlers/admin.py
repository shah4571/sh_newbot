
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import ADMIN_ID
from bot.utils import storage

@Client.on_message(filters.private & filters.user(ADMIN_ID))
async def admin_handler(client, message: Message):
    args = message.text.split()

    if message.text.startswith("/setrate") and len(args) == 3:
        try:
            country = args[1].upper()
            price = float(args[2])
            storage.set_rate(country, price)
            await message.reply(f"✅ Rate for {country} set to ${price}")
        except ValueError:
            await message.reply("❌ Invalid price. Example: /setrate BD 0.30")

    elif message.text.startswith("/setsession") and len(args) == 2:
        try:
            timeout = int(args[1])
            storage.set_session_timeout(timeout)
            await message.reply(f"✅ Session time set to {timeout} minutes.")
        except ValueError:
            await message.reply("❌ Invalid time. Example: /setsession 10")

    else:
        await message.reply("⚠️ Unknown admin command or wrong format.")
