from pyrogram import Client, filters
from pyrogram.types import Message

def init(app):
    @app.on_message(filters.command("support") & filters.private)
    async def support_handler(client: Client, message: Message):
        await message.reply_text(
            "🆘 Need Help?\n\n"
            "Contact support: @xrd_didox"
        )

