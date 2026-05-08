import os
import requests
from datetime import datetime, timedelta

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BASELINE_INDIA = 1100
BASELINE_FRANCE = 1250

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🔎 כאן בעתיד נחבר API אמיתי (Amadeus / Kiwi)
def search_flights():
    # סימולציה זמנית של תוצאה אמיתית
    return {
        "price": 980,
        "refundable": True,
        "stops": 1
    }

def check():
    flight = search_flights()

    price = flight["price"]
    refundable = flight["refundable"]
    stops = flight["stops"]

    if stops > 1:
        return

    if not refundable:
        return

    if price < BASELINE_INDIA:
        send(f"✈️ טיסה גמישה זולה יותר מאייר אינדיה: ${price}")

    if price < BASELINE_FRANCE:
        send(f"✈️ טיסה גמישה זולה יותר מאייר פראנס: ${price}")

if __name__ == "__main__":
    check()
