from pyrogram import Client, filters
from pyrogram.types import Message
from bot.utils import storage

def init(app):
    @app.on_message(filters.command("account") & filters.private)
    async def account_handler(client: Client, message: Message):
        uid = message.from_user.id
        info = storage.get_user_info(uid)

        if not info:
            return await message.reply_text("❌ You are not registered. Please press /start.")

        await message.reply_text(
            "🎫 Your user account in the robot:\n\n"
            f"👤 ID: `{uid}`\n"
            f"🥅 Totally success account: `{info.get('success', 0)}`\n"
            f"💰 Your balance: `${info.get('balance', 0.0):.2f}`\n"
            f"⏰ This post was taken in: `{info.get('joined', 'N/A')}`"
        )

