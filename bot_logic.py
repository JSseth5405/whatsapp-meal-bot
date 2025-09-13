
import json
from datetime import date, timedelta
from sqlalchemy.orm import Session
from models import Resident, MenuItem, Booking, SessionState
from utils.parsing import parse_meal, parse_relative_date, parse_int, normalize_phone, MEALS
from utils.timeutils import is_before_cutoff
from config import Config
from services.whatsapp import send_text, send_buttons

WELCOME = (
    "Hi! This is the {biz} canteen bot. You can type:\n"
    "- 'menu' to view upcoming menu\n"
    "- 'book' to book a meal\n"
    "- 'my bookings' to see your bookings\n"
    "- 'cancel' to cancel a booking"
)

def get_or_create_resident(db: Session, phone: str):
    res = db.query(Resident).filter_by(phone=phone).first()
    if not res:
        # unknown number -> create placeholder; in production, you may enforce pre-registered members only
        res = Resident(name="Member", phone=phone, unit_no="NA", is_opted_in=True)
        db.add(res)
        db.commit()
        db.refresh(res)
    return res

def get_state(db: Session, phone: str):
    st = db.query(SessionState).filter_by(phone=phone).first()
    if not st:
        st = SessionState(phone=phone, state="idle", context="{}")
        db.add(st)
        db.commit()
        db.refresh(st)
    return st

def set_state(db: Session, phone: str, state: str, context: dict):
    st = get_state(db, phone)
    st.state = state
    st.context = json.dumps(context)
    db.add(st)
    db.commit()

def handle_text_message(db: Session, wa_from: str, text: str):
    phone = normalize_phone(wa_from)
    resident = get_or_create_resident(db, phone)
    st = get_state(db, phone)
    t = text.strip().lower()

    if t in ["hi", "hello", "help", "start"]:
        send_buttons(
            phone,
            WELCOME.format(biz=Config.BUSINESS_NAME),
            [{"id":"BOOK","title":"Book"}, {"id":"MENU","title":"Menu"}, {"id":"MY","title":"My bookings"}]
        )
        return

    # Simple commands
    if t.startswith("menu"):
        send_menu_preview(db, phone)
        return

    if t.startswith("my"):
        send_my_bookings(db, phone)
        return

    if t.startswith("cancel"):
        start_cancel_flow(db, phone)
        return

    if t.startswith("book"):
        start_booking_flow(db, phone)
        return

    # Continue stateful flow
    if st.state == "booking_meal":
        meal = parse_meal(t)
        if meal not in MEALS:
            send_text(phone, "Please choose a meal: breakfast, lunch, or dinner.")
            return
        ctx = {"meal": meal}
        set_state(db, phone, "booking_date", ctx)
        send_text(phone, "For which day? (e.g., 'tomorrow' or YYYY-MM-DD)")
        return

    if st.state == "booking_date":
        d = parse_relative_date(t)
        if not d:
            send_text(phone, "Could not parse the date. Please say 'tomorrow' or YYYY-MM-DD.")
            return
        if not is_before_cutoff(d, Config.BOOKING_CUTOFF_HOURS):
            send_text(phone, f"Bookings must be at least {Config.BOOKING_CUTOFF_HOURS}h in advance.")
            set_state(db, phone, "idle", {})
            return
        ctx = json.loads(st.context); ctx["date"] = str(d)
        set_state(db, phone, "booking_qty", ctx)
        send_text(phone, "How many portions? (1-9)")
        return

    if st.state == "booking_qty":
        qty = max(1, min(9, parse_int(t, 1)))
        ctx = json.loads(st.context)
        meal = ctx["meal"]; d = date.fromisoformat(ctx["date"])
        # Save booking
        b = Booking(resident_id=resident.id, menu_date=d, meal=meal, qty=qty, status="booked")
        db.add(b); db.commit()
        send_text(phone, f"Booked {qty} {meal} for {d}. To cancel, reply 'cancel'. ✅")
        set_state(db, phone, "idle", {})
        return

    if st.state == "cancelling":
        # Expect format like 'cancel 123' or just '123'
        parts = t.split()
        bid = None
        for p in parts:
            if p.isdigit():
                bid = int(p)
                break
        if not bid:
            send_text(phone, "Please reply with the booking ID you want to cancel.")
            return
        b = db.query(Booking).filter_by(id=bid, resident_id=resident.id).first()
        if not b:
            send_text(phone, "Booking not found.")
            set_state(db, phone, "idle", {})
            return
        if b.status != "booked":
            send_text(phone, "That booking is not active.")
            set_state(db, phone, "idle", {})
            return
        if not is_before_cutoff(b.menu_date, Config.BOOKING_CUTOFF_HOURS):
            send_text(phone, f"Cancellation must be at least {Config.BOOKING_CUTOFF_HOURS}h in advance.")
            set_state(db, phone, "idle", {})
            return
        b.status = "cancelled"
        db.add(b); db.commit()
        send_text(phone, f"Cancelled booking {bid} for {b.meal} on {b.menu_date}.")
        set_state(db, phone, "idle", {})
        return

    # Fallback
    send_text(phone, "Sorry, I didn't get that. Type 'menu', 'book', 'my bookings', or 'cancel'.")

def start_booking_flow(db, phone):
    set_state(db, phone, "booking_meal", {})
    send_text(phone, "Which meal do you want to book? (breakfast/lunch/dinner)")

def start_cancel_flow(db, phone):
    set_state(db, phone, "cancelling", {})
    send_my_bookings(db, phone, prefix="Reply with the booking ID to cancel.")

def send_menu_preview(db, phone):
    from datetime import date, timedelta
    msgs = []
    for delta in [1,2]:  # show next 2 days as preview
        d = date.today() + timedelta(days=delta)
        items = db.query(MenuItem).filter_by(menu_date=d).order_by(MenuItem.meal).all()
        if items:
            body = f"Menu for {d}:\n"
            meals = {}
            for it in items:
                meals.setdefault(it.meal, []).append(it.dish + (" (veg)" if it.is_veg else " (non-veg)"))
            for meal, dishes in meals.items():
                body += f"- {meal.title()}: " + ", ".join(dishes) + "\n"
            msgs.append(body.strip())
    if msgs:
        send_text(phone, "\n\n".join(msgs))
    else:
        send_text(phone, "No upcoming menu has been set yet.")

def send_my_bookings(db, phone, prefix=None):
    from models import Resident, Booking
    res = db.query(Resident).filter_by(phone=phone).first()
    if not res:
        send_text(phone, "We couldn't find your profile.")
        return
    rows = db.query(Booking).filter_by(resident_id=res.id).order_by(Booking.created_at.desc()).limit(10).all()
    if not rows:
        send_text(phone, "You have no bookings yet.")
        return
    lines = [prefix] if prefix else []
    lines.append("Your recent bookings:")
    for b in rows:
        label = f"#{b.id} {b.meal} on {b.menu_date} — {b.qty}x — {b.status}"
        lines.append(label)
    send_text(phone, "\n".join(lines))
