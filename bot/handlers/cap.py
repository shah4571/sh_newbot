
from pyrogram.types import Message

async def cap_handler(client, message: Message):
    msg = (
        "🌍 Available Countries and Prices:\n\n"
        "🇮🇳 India - $0.15\n"
        "🇧🇩 Bangladesh - $0.20\n"
        "🇮🇩 Indonesia - $0.10"
    )
    await message.reply_text(msg)
