
# ✅ Client Setup (Attach Your WhatsApp Number & Go Live)

Hi! Here’s the plain‑English checklist to connect your WhatsApp Business number to this bot.
You can share this with any non‑tech teammate — it’s intentionally simple.

---

## 1) Get the WhatsApp Cloud API ready
- Log in to your **Meta Business** + **Developer** account.
- Create a **Developer App** (if you don’t have one) and add the **WhatsApp** product.
- In **WhatsApp → API Setup**, click **Add phone number**. Finish the OTP steps.
- You’ll get a **Phone Number ID**. Keep it handy.

> Using a number that already runs on the WhatsApp Business **app**? We need to **migrate** that number to the API first.
> Chat history doesn’t move; plan a short downtime. If you’re unsure, ask us and we’ll guide you.

---

## 2) Create a Permanent Access Token
- In **Business Settings → Users → System Users**, create a “system user” and grant WhatsApp permissions.
- Generate a **Permanent (long‑lived) Access Token**. Keep it secret and safe.

---

## 3) We deploy the bot for you
- We’ll put the bot on our server (or yours). There are two parts:
  1. **Web** (receives messages) → URL will look like `https://your-bot-domain/webhook`
  2. **Worker** (sends the daily menu at 9:00 AM)
- We’ll set your **Access Token** + **Phone Number ID** as environment variables.

---

## 4) Point WhatsApp Webhook to the bot
- In the **Developer Dashboard → WhatsApp → Webhooks**:
  - Callback URL: `https://your-bot-domain/webhook`
  - Verify Token: we’ll give you a simple secret (e.g., `my-verify-token`)
  - Subscribe to **messages** events
- That’s it. The bot replies to users on WhatsApp.

---

## 5) Quick test
- From your phone, message your business number with **“hi”**.
- Try: `menu`, `book`, `my bookings`, `cancel`.

> Want automatic daily menu messages? That’s the “Worker”. We’ll keep it running.
> You can pause it any time.

---

## 6) Updating your menu & residents
- You can start by sending us your **menu and residents in Excel**. We’ll load them.
- Later, we can add a small admin page if you want to update menus yourself.

---

**Done.** You’re live 🎉. If anything feels confusing, ping us — we’ll simplify further.
