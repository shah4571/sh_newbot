
from pyrogram.types import Message
from pyrogram import Client, filters

@Client.on_message(filters.command("support") & filters.private)
async def support_handler(client, message: Message):
    await message.reply_text(
        "🆘 For help contact: @xrd_didox",
        quote=True
    )
