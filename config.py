
import os

class Config:
    ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
    PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WABA_ID = os.getenv("WHATSAPP_WABA_ID")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "verifytoken")
    PORT = int(os.getenv("PORT", "5000"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    DAILY_BROADCAST_HOUR = int(os.getenv("DAILY_BROADCAST_HOUR", "9"))
    BOOKING_CUTOFF_HOURS = int(os.getenv("BOOKING_CUTOFF_HOURS", "24"))
    MAX_BOOKING_DAYS_AHEAD = int(os.getenv("MAX_BOOKING_DAYS_AHEAD", "7"))
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Canteen")
