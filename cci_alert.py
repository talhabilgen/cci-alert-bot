# cci_alert.py
import time
import os
import requests
import pandas as pd
import pandas_ta as ta
from tradingview_ta import TA_Handler, Interval, Exchange

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
SYMBOL = "XAUUSD"
EXCHANGE = "OANDA"
SCREENER = "forex"
INTERVAL = Interval.INTERVAL_5_MINUTES

last_signal = None

# =====================
# Ana döngü
# =====================
while True:
    try:
        handler = TA_Handler(
            symbol=SYMBOL,
            screener=SCREENER,
            exchange=EXCHANGE,
            interval=INTERVAL
        )

        analysis = handler.get_analysis()
        # Close fiyatları al
        close_prices = analysis.indicators['close'] if 'close' in analysis.indicators else None

        # Eğer close fiyat yoksa, son bar fiyatını al
        if close_prices is None:
            close_prices = [analysis.indicators['close']]

        df = pd.DataFrame(close_prices, columns=['close'])
        # Fake High/Low ekle, çünkü pandas_ta CCI için lazım
        df['high'] = df['close']
        df['low'] = df['close']

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
                msg = "CCI -100 yukarı kesildi! {} (5m)\nGüncel CCI: {:.2f}".format(SYMBOL, current)
                send_telegram_message(msg)
                print(msg)
                last_signal = "cross_up"
        else:
            last_signal = None

    except Exception as e:
        print("Hata:", e)

    # 5 dakikada bir kontrol et
    time.sleep(300)
