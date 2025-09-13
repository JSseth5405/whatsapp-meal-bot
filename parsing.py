
import re
from datetime import date, timedelta

MEALS = ["breakfast", "lunch", "dinner"]

def normalize_phone(wa_id):
    # WhatsApp 'from' wa_id is MSISDN without +
    return wa_id

def parse_int(s, default=1):
    try:
        return int(s)
    except Exception:
        return default

def parse_meal(text):
    text = text.lower()
    for m in MEALS:
        if m in text:
            return m
    return None

def parse_relative_date(text):
    text = text.lower().strip()
    if "today" in text:
        return date.today()
    if "tomorrow" in text:
        return date.today() + timedelta(days=1)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        y, mm, dd = map(int, m.groups())
        return date(y, mm, dd)
    return None
