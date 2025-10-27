# cci_alert.py
import time
import os
import requests
import pandas as pd
import pandas_ta as ta
from tvDatafeed import TvDatafeed, Interval

# =====================
# Telegram ayarları
# =====================
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")  # Render Secrets
CHAT_ID = os.environ.get("TG_CHAT_ID")      # Render Secrets
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram_message(msg):
    """Telegram’a mesaj gönderir"""
    requests.post(TELEGRAM_URL, data={"chat_id": CHAT_ID, "text": msg})

# =====================
# TradingView ayarları
# =====================
tv = TvDatafeed()  # Kullanıcı girişi opsiyonel, anonymous olarak çalışır

SYMBOL = "XAUUSD"
EXCHANGE = "OANDA"  # TradingView’daki OANDA verisi
INTERVAL = Interval.in_5_minute
N_BARS = 300  # son 300 barı çek

last_signal = None

# =====================
# Ana döngü
# =====================
while True:
    try:
        # XAUUSD verisini çek
        df = tv.get_hist(symbol=SYMBOL, exchange=EXCHANGE, int_
