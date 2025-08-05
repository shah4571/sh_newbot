
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.utils import storage

@Client.on_message(filters.command("account") & filters.private)
async def account_handler(client, message: Message):
    uid = message.from_user.id
    info = storage.get_user_info(uid)

    msg = (
        "🎫 Your user account in the robot:\n\n"
        f"👤 ID: {uid}\n"
        f"🥅 Totally success account: {info['success']}\n"
        f"💰 Your balance: {info['balance']} USD\n"
        f"⏰ This post was taken in {info['joined']}"
    )

    await message.reply_text(msg)
