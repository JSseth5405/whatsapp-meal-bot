
from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from config import Config
from db import SessionLocal
from models import Resident, MenuItem
from services.whatsapp import send_text

def send_tomorrow_menu():
    db = SessionLocal()
    try:
        d = date.today() + timedelta(days=1)
        items = db.query(MenuItem).filter_by(menu_date=d).all()
        if not items:
            print("No menu for", d)
            return
        by_meal = {}
        for it in items:
            by_meal.setdefault(it.meal, []).append(it.dish + (" (veg)" if it.is_veg else " (non-veg)"))
        body = f"{Config.BUSINESS_NAME}: Menu for {d}\n"
        for meal, dishes in by_meal.items():
            body += f"- {meal.title()}: " + ", ".join(dishes) + "\n"
        body += "\nReply 'book' to reserve or 'cancel' to cancel. Note: cutoff " + str(Config.BOOKING_CUTOFF_HOURS) + "h."
        # Broadcast to all opted-in residents
        for r in db.query(Resident).filter_by(is_opted_in=True, is_active=True).all():
            try:
                send_text(r.phone, body)
            except Exception as e:
                print("Failed to send to", r.phone, e)
    finally:
        db.close()

def start_scheduler():
    sched = BackgroundScheduler(timezone=timezone(Config.TIMEZONE))
    # Every day at the configured hour
    sched.add_job(send_tomorrow_menu, "cron", hour=Config.DAILY_BROADCAST_HOUR, minute=0)
    sched.start()
    print("Scheduler started.")

if __name__ == "__main__":
    start_scheduler()
    import time
    while True:
        time.sleep(3600)
