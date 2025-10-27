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
        df = tv.get_hist(symbol=SYMBOL, exchange=EXCHANGE, interval=INTERVAL, n_bars=N_BARS)
        if df.empty:
            print("Veri alınamadı, 1 dakika bekleniyor...")
            time.sleep(60)
            continue

        # CCI hesapla
        df['CCI'] = ta.cci(df['high'], df['low'], df['close'], length=25)

        cci = df['CCI'].dropna()
        if len(cci) < 2:
            time.sleep(60)
            continue

        prev = cci.iloc[-2]
        current = cci.iloc[-1]

        # -100 seviyesini aşağıdan yukarı keserse
        if prev < -100 and current > -100:
            if last_signal != "cross_up":
                msg = f"🚀 CCI -100 yukarı kesildi! {SYMBOL} (5m)\nGüncel CCI: {round(current,2)}"
                send_telegram_message(msg)
                print(msg)
                last_signal = "cross_up"
        else:
            last_signal = None

    except Exception as e:
        print("Hata:", e)

    # 5 dakikada bir kontrol et
    time.sleep(300)
