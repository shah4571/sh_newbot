
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils import storage, converter
from config import CHANNEL_ID
import random

async def withdraw_handler(client, message: Message):
    uid = message.from_user.id
    info = storage.get_user_info(uid)
    trx_amount = converter.usd_to_trx(info['balance'])
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT (Bep 20)", callback_data="usdt")],
        [InlineKeyboardButton("TRX", callback_data="trx")],
        [InlineKeyboardButton("BKASH", callback_data="bkash")]
    ])
    await message.reply_text(f"""🎫 Your user account in the robot:

👤ID: {uid}
🥅  Totally success account : {info['success']}
💰 Your balance: {info['balance']} USD
⏰ This post was taken in {info['joined']}
""", reply_markup=keyboard)

    @client.on_callback_query()
    async def on_select(client, callback_query):
        method = callback_query.data
        await callback_query.message.reply(f"Okay. Send your wallet address ({method.upper()})")

        @client.on_message(filters.text & filters.private)
        async def address_input(client, addr_msg):
            trans_id = f"TC{random.randint(1000000000,9999999999)}"
            await client.send_message(CHANNEL_ID, f"""
- - Withdrawal successful.

Trans No : {trans_id}
- Your balance : {info['balance']} USD
- Currency : {method.upper()}
- Withdrawal amount  : {trx_amount} TRX
- Address : {addr_msg.text}

- Transaction ID :
636e4d0ce1b74b44b4fe0c6f4c9919c9
""")
            await addr_msg.reply("✅ Withdrawal request submitted successfully.")
            storage.reset_balance(uid)
