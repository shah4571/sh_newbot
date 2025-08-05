
from pyrogram.types import Message
from bot.utils import storage

async def admin_handler(client, message: Message):
    args = message.text.split()
    if message.text.startswith("/setrate") and len(args) == 3:
        country = args[1].upper()
        price = float(args[2])
        storage.set_rate(country, price)
        await message.reply(f"✅ Rate for {country} set to ${price}")
    elif message.text.startswith("/setsession") and len(args) == 2:
        storage.set_session_timeout(int(args[1]))
        await message.reply("✅ Session time set.")
