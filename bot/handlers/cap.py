from pyrogram import Client, filters
from pyrogram.types import Message
from bot.utils import storage

def init(app):
    @app.on_message(filters.command("cap") & filters.private)
    async def cap_handler(client: Client, message: Message):
        rates = storage.get_country_rates()

        if not rates:
            await message.reply_text("❌ No countries are currently available.")
            return

        response = "🌍 Available Countries:\n\n"
        for country, price in rates.items():
            response += f"🇺🇳 Country: `{country}`  —  💰 Price: ${price:.2f}\n"

        await message.reply_text(response)

