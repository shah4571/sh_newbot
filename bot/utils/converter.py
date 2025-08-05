
from config import TRX_RATE

def usd_to_trx(usd):
    return round(usd * TRX_RATE, 2)
