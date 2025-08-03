# Telegram Session Generator Bot

A fully automated Telegram bot that:
- Accepts phone numbers from users
- Sends OTP via Telethon
- Verifies the account with optional 2FA
- Saves and uploads session files to a private channel
- Handles per-country pricing and balance
- Allows withdrawals via various methods

### Commands

- `/start` — Restart and enter phone number
- `/cap` — See available countries and prices
- `/account` — View account info and balance
- `/withdraw` — Request withdrawal
- `/support` — Contact support

### Deployment

```bash
pip install -r requirements.txt
python bot.py
```