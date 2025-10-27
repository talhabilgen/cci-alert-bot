import time
import requests
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# =====================
# Telegram ayarları
# =====================
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram_message(message):
    """Telegram’a mesaj gönderir"""
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(TELEGRAM_URL, data=data)

def get_cci_data():
    """CCI(25) hesapla"""
    df = yf.download("XAUUSD=X", interval="5m", period="2d")
    df["CCI"] = ta.cci(df["High"], df["Low"], df["Close"], length=25)
    return df

last_signal = None

while True:
    df = get_cci_data()
    cci = df["CCI"].dropna()
    
    if len(cci) < 2:
        time.sleep(60)
        continue

    prev = cci.iloc[-2]
    current = cci.iloc[-1]

    # -100'ü aşağıdan yukarı keserse
    if prev < -100 and current > -100:
        if last_signal != "cross_up":
            send_telegram_message(f"🚀 CCI -100 yukarı kesildi! XAUUSD (5m)\nGüncel CCI: {round(current,2)}")
            last_signal = "cross_up"
    else:
        last_signal = None

    # 5 dakikada bir kontrol et
    time.sleep(300)
