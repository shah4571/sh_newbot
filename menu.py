from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ফেইক ইউজার ডেটা (প্রোডাকশনে ডাটাবেজ ব্যবহার করো)
user_data = {
    "balance": 10.5,
    "success_count": 3,
    "joined_at": datetime.now()
}

SUPPORT_USERNAME = "xrd_didox"  # তোমার সাপোর্ট ইউজারনেম


@Client.on_message(filters.command("start"))
async def start(client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 Menu", callback_data="menu")]
        ]
    )
    await message.reply("👋 Welcome! Use the menu below.", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("menu"))
async def menu(client, callback):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌐 Capacity", callback_data="cap")],
            [InlineKeyboardButton("🎰 Check - Balance", callback_data="account")],
            [InlineKeyboardButton("💸 Withdraw Accounts", callback_data="withdraw")],
            [InlineKeyboardButton("🆘 Need Help?", callback_data="support")]
        ]
    )
    await callback.message.edit_text("📲 Choose an option:", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("cap"))
async def cap_handler(client, callback):
    await callback.message.edit_text(
        "🌐 Available Countries:\n\n🇧🇩 Bangladesh - $0.30\n🇮🇳 India - $0.25\n🇵🇭 Philippines - $0.35",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]])
    )


@Client.on_callback_query(filters.regex("account"))
async def account_handler(client, callback):
    user_id = callback.from_user.id
    joined = user_data["joined_at"].strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"🎫 Your user account in the robot:\n\n"
        f"👤 ID: {user_id}\n"
        f"🥅 Totally success account: {user_data['success_count']}\n"
        f"💰 Your balance: ${user_data['balance']:.2f}\n"
        f"⏰ This post was taken in {joined}"
    )
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))


@Client.on_callback_query(filters.regex("withdraw"))
async def withdraw_handler(client, callback):
    user_id = callback.from_user.id
    joined = user_data["joined_at"].strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"🎫 Your user account in the robot:\n\n"
        f"👤 ID: {user_id}\n"
        f"🥅 Totally success account: {user_data['success_count']}\n"
        f"💰 Your balance: ${user_data['balance']:.2f}\n"
        f"⏰ This post was taken in {joined}\n\n"
        f"💵 Choose withdrawal method:"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💳 USDT (BEP20)", callback_data="withdraw_usdt")],
            [InlineKeyboardButton("💸 TRX", callback_data="withdraw_trx")],
            [InlineKeyboardButton("📱 BKASH", callback_data="withdraw_bkash")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("support"))
async def support_handler(client, callback):
    await callback.message.edit_text(
        f"🆘 For help, contact: @{SUPPORT_USERNAME}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]])
    )