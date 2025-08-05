
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("cap") & filters.private)
async def cap_handler(client, message: Message):
    msg = (
        "🌍 Available Countries and Prices:\n\n"
        "🇮🇳 India - $0.15\n"
        "🇧🇩 Bangladesh - $0.20\n"
        "🇮🇩 Indonesia - $0.10\n"
        "🇵🇰 Pakistan - $0.18\n"
        "🇳🇵 Nepal - $0.12\n"
        "🇱🇰 Sri Lanka - $0.22"
    )
    await message.reply_text(msg)
