
import os, json
from flask import Flask, request, jsonify
from config import Config
from db import Base, engine, SessionLocal
from models import *
from bot_logic import handle_text_message
from services.whatsapp import send_text, send_buttons

app = Flask(__name__)

# Initialize tables
Base.metadata.create_all(bind=engine)

@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == Config.VERIFY_TOKEN:
        return challenge, 200
    return "forbidden", 403

@app.post("/webhook")
def inbound():
    data = request.get_json(force=True, silent=True) or {}
    # Meta delivers events under entry[] -> changes[] -> value
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for m in messages:
                    from_wa = m.get("from")
                    msg_type = m.get("type")
                    text = None
                    if msg_type == "text":
                        text = m["text"]["body"]
                    elif msg_type == "interactive":
                        interactive = m.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            text = interactive["button_reply"]["id"]
                        elif interactive.get("type") == "list_reply":
                            text = interactive["list_reply"]["id"]
                    else:
                        text = "help"
                    # Handle with DB session
                    db = SessionLocal()
                    try:
                        handle_text_message(db, from_wa, text)
                    finally:
                        db.close()
    except Exception as e:
        print("Webhook error:", e)
    return jsonify({"status":"ok"})

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
