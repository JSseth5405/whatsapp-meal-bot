
import requests
from config import Config

API_BASE = "https://graph.facebook.com/v20.0"

def send_text(to_phone, text):
    url = f"{API_BASE}/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    try:
        r.raise_for_status()
    except Exception as e:
        print("WA send error:", r.text)
        raise
    return r.json()

def send_buttons(to_phone, body_text, buttons):
    # buttons is list of {"id": "BOOK", "title": "Book"}
    url = f"{API_BASE}/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": [
                {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in buttons
            ]}
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    try:
        r.raise_for_status()
    except Exception:
        print("WA send error:", r.text)
        raise
    return r.json()
