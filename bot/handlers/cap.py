
from pyrogram.types import Message

async def cap_handler(client, message: Message):
    msg = "🌍 Available Countries and Prices:

🇮🇳 India - $0.15
🇧🇩 Bangladesh - $0.20
🇮🇩 Indonesia - $0.10"
    await message.reply_text(msg)
