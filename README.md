
# 🍽️ WhatsApp Meal Booking Bot — Plug‑and‑Play

Hey! This repo gives you a **ready-to-run WhatsApp bot** for meal bookings and cancellations.
It's built with **Python + Flask** and the **WhatsApp Cloud API**. You can demo it **today** with
dummy data, and go **live** once a business connects its WhatsApp number.

> TL;DR: create a venv → install deps → copy `.env.example` to `.env` → **run `python app.py`** → test.
> No real data? Run **`python scripts/make_dummy_data.py`** and you're good to demo.

---

## 🚀 What it does (v1)
- Show upcoming **menu** (next two days by default).
- **Book** a meal (breakfast/lunch/dinner) with quantity.
- **See** your recent bookings.
- **Cancel** a booking (if it's not too close to service time).
- A **daily broadcast** (9:00 AM IST by default) that sends **tomorrow’s menu** to all opted-in residents.

**Rules you can tweak in `.env`:**
- `BOOKING_CUTOFF_HOURS` (default 24 hours before service date)
- `TIMEZONE` (default Asia/Kolkata)
- `DAILY_BROADCAST_HOUR` (default 9 — that’s 9 AM local time)

---

## 🧰 What you need
- **Python 3.9+** installed
- (Optional for going live) A Meta Developer App with **WhatsApp Cloud API** enabled and a **WhatsApp Business number**
- (Optional for local webhook testing) **ngrok** or any HTTPS tunnel

You can still **test locally without WhatsApp** using the `curl` commands below.

---

## 🏁 Quick Start (local)
**Terminal (Mac/Windows/Linux):**
```bash
cd /path/to/whatsapp-meal-bot

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
```

Open `.env` and fill only if you want to hit WhatsApp for real (you can skip for local logic tests).
At minimum later you’ll set:
```
WHATSAPP_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID
VERIFY_TOKEN=some_secret_string_you_choose
```

**No real data yet?** Create nice demo data:
```bash
python scripts/make_dummy_data.py
```

Start the bot:
```bash
python app.py
```
- Your server is now on **http://127.0.0.1:5000** (keep this window running).

---

## 🧪 Test without WhatsApp (fake inbound via curl)
Open a **new** terminal tab/window and paste:

```bash
# Say "hi"
curl -s -X POST http://127.0.0.1:5000/webhook -H "Content-Type: application/json" -d '{
  "entry": [{"changes": [{"value": {"messages": [{
    "from": "919999999999", "type": "text", "text": {"body": "hi"}
  }]}}]}]}'

# Show menu
curl -s -X POST http://127.0.0.1:5000/webhook -H "Content-Type: application/json" -d '{
  "entry": [{"changes": [{"value": {"messages": [{
    "from": "919999999999", "type": "text", "text": {"body": "menu"}
  }]}}]}]}'

# Start booking
curl -s -X POST http://127.0.0.1:5000/webhook -H "Content-Type: application/json" -d '{
  "entry": [{"changes": [{"value": {"messages": [{
    "from": "919999999999", "type": "text", "text": {"body": "book"}
  }]}}]}]}'
```

(Repeat the `curl` with the next replies like `breakfast`, `tomorrow`, `2` to complete a full booking flow.)

---

## 📲 Connect a real WhatsApp number (when ready)
**High level:** add a phone number to your **WhatsApp Business Account**, generate a **Permanent Access Token**,
deploy the app somewhere public (Render/Railway/any VPS), and point the WhatsApp **Webhook** to `https://your-domain/webhook`.
Then message your business number from a phone and say “hi”.

There’s a friendly **Client Steps** sheet in `docs/CLIENT_STEPS.md` you can share with a business so they can
attach their number and go live without headaches.

---

## 🌐 Expose your local server (for webhook verify)
If you want to verify the webhook locally:
```bash
# new terminal tab
ngrok http 5000
```
Copy the HTTPS URL (looks like `https://xxxx.ngrok-free.app`) and use it in the WhatsApp **Webhook** config as:
```
https://xxxx.ngrok-free.app/webhook
```
The app already supports the verification handshake (`hub.challenge`).

---

## ☁️ Deploy (easy path)
**Render/Railway** style (two processes):

- **Web service** (inbound messages):  
  Start command → `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

- **Worker** (daily broadcast):  
  Start command → `python scheduler.py`

Set environment variables from `.env.example` in your host’s dashboard.

---

## 🧱 Folder tour (what lives where)
```
whatsapp-meal-bot/
├── app.py                 # Flask app with /webhook + verification
├── bot_logic.py           # Chat flow (menu, book, cancel, my bookings)
├── services/whatsapp.py   # WhatsApp Cloud API (send text/buttons)
├── models.py              # SQLAlchemy models (Resident, MenuItem, Booking, SessionState)
├── db.py, config.py       # DB engine + config (reads .env)
├── scheduler.py           # Daily broadcast (menu for tomorrow at 09:00 local)
├── utils/                 # parsing + time helpers
├── scripts/
│   └── make_dummy_data.py # creates demo residents + a 7‑day menu
├── data/
│   ├── residents.csv      # sample columns
│   └── menu.csv           # sample columns
├── seed.py                # loads CSVs into the DB
├── requirements.txt       # pip deps (incl. gunicorn)
├── Dockerfile, Procfile   # for Docker or PaaS deploy
├── .env.example           # copy to .env and fill
└── docs/
    └── CLIENT_STEPS.md    # one‑pager to share with a business
```

---

## 🛠️ Tweak the behavior
- Change **cutoff** / **timezone** / **broadcast hour** in `.env`.
- Change wording of messages in `bot_logic.py`.
- Add capacity limits per meal (e.g., count bookings by `menu_date`+`meal` before inserting).

---

## 🧯 Troubleshooting (quick)
- **Webhook verify fails?** Double‑check the HTTPS URL and make sure `VERIFY_TOKEN` in the Meta dashboard exactly
  matches your `.env`. Restart the app after editing `.env`.
- **No replies?** Look at your terminal where `python app.py` is running—errors show there. Check that the number
  you’re messaging is the **business/test** number connected to your WABA.
- **Reset data?** Stop the server, delete `data.db`, re‑run `python seed.py` or `python scripts/make_dummy_data.py`.

---


