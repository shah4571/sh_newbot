from pyrogram import Client, filters

from pyrogram.types import Message

from bot.config import ADMIN_ID

from bot.utils import storage



def init(app):

    @app.on_message(filters.command("setrate") & filters.private)

    async def setrate_handler(client: Client, message: Message):

        if message.from_user.id != ADMIN_ID:

            return await message.reply_text("❌ You are not authorized.")



        try:

            _, country_code, price = message.text.strip().split()

            price = float(price)

        except:

            return await message.reply_text("Usage: /setrate <country_code> <price>")



        storage.set_country_rate(country_code, price)

        await message.reply_text(f"✅ Rate for `{country_code}` set to ${price:.2f}")



    @app.on_message(filters.command("setsession") & filters.private)

    async def setsession_handler(client: Client, message: Message):

        if message.from_user.id != ADMIN_ID:

            return await message.reply_text("❌ You are not authorized.")



        try:

            _, seconds = message.text.strip().split()

            seconds = int(seconds)

        except:

            return await message.reply_text("Usage: /setsession <seconds>")



        storage.set_verify_time(seconds)

        await message.reply_text(f"✅ Verification time set to {seconds} seconds")
