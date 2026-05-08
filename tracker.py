import os
import requests
import json
from datetime import datetime, timedelta

# --- secrets ---
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
KEY = os.environ["AMADEUS_KEY"]
SECRET = os.environ["AMADEUS_SECRET"]

# --- קובץ שמירת מחיר ---
STATE_FILE = "state.json"

BASELINE_INDIA = 1100
BASELINE_FRANCE = 1250

# --- טלגרם ---
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# --- שמירת מחיר נמוך ---
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"lowest": 999999}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# --- טוקן ל־Amadeus ---
def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": KEY,
        "client_secret": SECRET
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

# --- חיפוש טיסות ---
def search(token):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    params = {
        "originLocationCode": "TLV",
        "destinationLocationCode": "HND",
        "departureDate": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "adults": 1,
        "currencyCode": "USD",
        "max": 5,
        "nonStop": False
    }

    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, headers=headers, params=params)
    return r.json()

# --- בדיקה חכמה ---
def check():
    state = load_state()
    token = get_token()
    data = search(token)

    try:
        offer = data["data"][0]
        price = float(offer["price"]["total"])
        segments = offer["itineraries"][0]["segments"]
        stops = len(segments) - 1

        # פילטרים
        if stops > 1:
            return

        # רק טיסות סבירות
        if price > 5000:
            return

        # בדיקת ירידה אמיתית
        if price < state["lowest"]:
            state["lowest"] = price
            save_state(state)

            send(f"✈️ ירידת מחיר אמיתית!\nמחיר חדש: ${price}\nעצירות: {stops}")

        # השוואה למחירים שלך
        if price < BASELINE_INDIA:
            send(f"✈️ זול יותר מאייר אינדיה: ${price}")

        if price < BASELINE_FRANCE:
            send(f"✈️ זול יותר מאייר פראנס: ${price}")

    except Exception as e:
        send(f"שגיאה: {e}")

if __name__ == "__main__":
    check()
