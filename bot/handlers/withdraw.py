
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.utils import storage, converter
from bot.config import CHANNEL_ID
import random

# Dictionary to track which user is in which withdraw stage
pending_withdraw = {}

@Client.on_message(filters.command("withdraw") & filters.private)
async def withdraw_handler(client, message: Message):
    uid = message.from_user.id
    info = storage.get_user_info(uid)
    trx_amount = converter.usd_to_trx(info['balance'])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT (Bep 20)", callback_data="withdraw_usdt")],
        [InlineKeyboardButton("TRX", callback_data="withdraw_trx")],
        [InlineKeyboardButton("BKASH", callback_data="withdraw_bkash")]
    ])

    await message.reply_text(f"""🎫 Your user account in the robot:

👤ID: {uid}
🥅  Totally success account : {info['success']}
💰 Your balance: {info['balance']} USD
⏰ This post was taken in {info['joined']}
""", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^withdraw_"))
async def handle_withdraw_selection(client, callback_query: CallbackQuery):
    uid = callback_query.from_user.id
    method = callback_query.data.replace("withdraw_", "")
    pending_withdraw[uid] = method  # Store selected method

    await callback_query.message.reply_text(
        f"💳 Okay. Send your wallet address or number for {method.upper()}."
    )
    await callback_query.answer()

@Client.on_message(filters.text & filters.private)
async def receive_wallet_address(client, message: Message):
    uid = message.from_user.id
    if uid not in pending_withdraw:
        return  # Not in withdrawal process

    method = pending_withdraw.pop(uid)  # Remove user from pending
    info = storage.get_user_info(uid)
    trx_amount = converter.usd_to_trx(info['balance'])
    trans_id = f"TC{random.randint(1000000000, 9999999999)}"

    await client.send_message(
        CHANNEL_ID,
        f"""
📤 Withdrawal Request Received

🆔 User ID: {uid}
💰 Balance: {info['balance']} USD
💱 Method: {method.upper()}
🎯 Withdraw Amount: {trx_amount} TRX
🏦 Address/Number: {message.text}
🔐 Transaction ID: {trans_id}
"""
    )

    await message.reply_text("✅ Withdrawal request submitted successfully.")
    storage.reset_balance(uid)
