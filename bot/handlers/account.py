
from pyrogram.types import Message
from bot.utils import storage

async def account_handler(client, message: Message):
    uid = message.from_user.id
    info = storage.get_user_info(uid)
    await message.reply_text(f"""🎫 Your user account in the robot:

👤ID: {uid}
🥅  Totally success account : {info['success']}
💰 Your balance: {info['balance']} USD
⏰ This post was taken in {info['joined']}
""")
