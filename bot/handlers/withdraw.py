from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils import storage, converter
from bot.config import ADMIN_ID
import random
import string

# Stages to track user's withdraw flow
user_withdraw_stage = {}
user_withdraw_currency = {}

def init(app):
    @app.on_message(filters.command("withdraw") & filters.private)
    async def withdraw_command(client: Client, message: Message):
        uid = message.from_user.id
        info = storage.get_user_info(uid)

        if not info or info.get("balance", 0) <= 0:
            return await message.reply_text("❌ You have no balance to withdraw.")

        text = (
            "🎫 Your user account in the robot:\n\n"
            f"👤 ID: `{uid}`\n"
            f"🥅 Totally success account: `{info.get('success', 0)}`\n"
            f"💰 Your balance: `${info.get('balance', 0):.2f}`\n"
            f"⏰ This post was taken in: `{info.get('joined', 'N/A')}`\n\n"
            "Please select a withdrawal method:"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("USDT (BEP20)", callback_data="withdraw_usdt")],
                [InlineKeyboardButton("TRX", callback_data="withdraw_trx")],
                [InlineKeyboardButton("BKASH", callback_data="withdraw_bkash")],
            ]
        )
        user_withdraw_stage[uid] = "awaiting_currency"
        await message.reply_text(text, reply_markup=keyboard)

    @app.on_callback_query()
    async def withdraw_callback(client: Client, callback_query):
        uid = callback_query.from_user.id
        data = callback_query.data

        if uid not in user_withdraw_stage:
            return await callback_query.answer("Please send /withdraw first.")

        if user_withdraw_stage[uid] == "awaiting_currency":
            if data not in ("withdraw_usdt", "withdraw_trx", "withdraw_bkash"):
                return await callback_query.answer("Invalid option.")

            currency = data.split("_")[1].upper()
            user_withdraw_currency[uid] = currency
            user_withdraw_stage[uid] = "awaiting_address"

            await callback_query.message.edit_text(
                f"Okay. Send your wallet address for {currency}."
            )
            await callback_query.answer()

        else:
            await callback_query.answer("Please follow the withdrawal process.")

    @app.on_message(filters.private & filters.text)
    async def withdraw_address_handler(client: Client, message: Message):
        uid = message.from_user.id
        if user_withdraw_stage.get(uid) != "awaiting_address":
            return

        address = message.text.strip()
        currency = user_withdraw_currency.get(uid)
        info = storage.get_user_info(uid)
        balance = info.get("balance", 0)

        if not currency or balance <= 0:
            user_withdraw_stage.pop(uid, None)
            user_withdraw_currency.pop(uid, None)
            return await message.reply_text("❌ Withdrawal process error. Please try again.")

        # Generate a fake transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

        # Convert balance to TRX for report if needed
        trx_amount = balance
        if currency != "TRX":
            trx_amount = converter.usd_to_trx(balance)

        # Compose report for admin channel
        report = (
            "- - Withdrawal successful.\n\n"
            f"Trans No : {transaction_id}\n"
            f"- Your balance : ${balance:.2f}\n"
            f"- Currency : {currency}\n"
            f"- Withdrawal amount : {trx_amount:.2f} TRX equivalent\n"
            f"- Address : {address}\n\n"
            f"- Transaction ID : {transaction_id}"
        )

        # Send report to admin channel
        await client.send_message(
            chat_id=ADMIN_ID,
            text=report
        )

        # Reset user withdraw state
        user_withdraw_stage.pop(uid, None)
        user_withdraw_currency.pop(uid, None)

        # Reset user balance to zero after withdraw
        storage.update_balance(uid, -balance)

        await message.reply_text(
            "✅ Withdrawal request sent successfully!\n\n"
            f"Transaction ID: {transaction_id}"
        )

