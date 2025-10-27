# cci_alert.py
import time
import os
import requests
import pandas as pd
import pandas_ta as ta
from tradingview_ta import TA_Handler, Interval, Exchange
from flask import Flask
import threading

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
# Flask web server (Render port requirement)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "CCI Bot Running"

# =====================
# Bot loop
# =====================
def bot_loop():
    SYMBOL = "XAUUSD"
    EXCHANGE = "OANDA"
    SCREENER = "forex"
    INTERVAL = Interval.INTERVAL_5_MINUTES

    last_signal = None

    while True:
        try:
            # TradingView_TA verisi
            handler = TA_Handler(
                symbol=SYMBOL,
                screener=SCREENER,
                exchange=EXCHANGE,
                interval=INTERVAL
            )

            analysis = handler.get_analysis()
            # Close fiyatları al (indikator olarak gelmeyebilir)
            close_prices = [analysis.indicators['close']]
            df = pd.DataFrame(close_prices, columns=['close'])
            # Fake high/low ekle (CCI için lazım)
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

            # -100 seviyesini aşağıdan yukarı keserse Telegram bildir
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

# Bot loop'u thread olarak başlat
threading.Thread(target=bot_loop, daemon=True).start()

# Flask app'i çalıştır (Render port requirement)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
