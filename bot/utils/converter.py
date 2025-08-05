from bot.config import TRX_RATE

def usd_to_trx(usd_amount):
    return round(float(usd_amount) * TRX_RATE, 2)
