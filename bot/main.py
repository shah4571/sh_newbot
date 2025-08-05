
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH, ADMIN_ID
from bot.handlers import start, cap, account, withdraw, support, admin

app = Client("session_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

app.add_handler(filters.command("start") & filters.private, start.start_handler)
app.add_handler(filters.command("cap") & filters.private, cap.cap_handler)
app.add_handler(filters.command("account") & filters.private, account.account_handler)
app.add_handler(filters.command("withdraw") & filters.private, withdraw.withdraw_handler)
app.add_handler(filters.command("support") & filters.private, support.support_handler)
app.add_handler(filters.command(["setrate", "setsession"]) & filters.user(ADMIN_ID), admin.admin_handler)

print("🤖 Bot is running...")
app.run()
