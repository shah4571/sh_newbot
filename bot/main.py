from pyrogram import Client
from bot.config import API_ID, API_HASH, BOT_TOKEN
from bot.handlers import start, cap, account, withdraw, support, admin

app = Client("session_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# হ্যান্ডলারগুলো ইনিশিয়ালাইজ করো
start.init(app)
cap.init(app)
account.init(app)
withdraw.init(app)
support.init(app)
admin.init(app)

# main execution guard - এটা অবশ্যই এই রকম লিখতে হবে
if name == "main":
    app.run()
