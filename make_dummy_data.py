
# scripts/make_dummy_data.py
from datetime import date, timedelta
from db import Base, engine, SessionLocal
from models import Resident, MenuItem

DAYS = 7
BREAKFASTS = ["Poha", "Upma", "Idli Sambar", "Masala Dosa", "Aloo Paratha", "Oats Bowl", "Chole Kulche"]
LUNCHES    = ["Dal Tadka", "Jeera Rice", "Paneer Butter Masala", "Veg Pulao", "Rajma Chawal", "Kadhi Chawal", "Mix Veg"]
DINNERS    = ["Chole Bhature", "Veg Biryani", "Palak Paneer", "Khichdi", "Pasta Arrabbiata", "Hakka Noodles", "Pav Bhaji"]

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Add two demo residents (change phone to yours to receive real messages)
        if not db.query(Resident).first():
            db.add_all([
                Resident(unit_no="A-101", name="Test User 1", phone="919999999999", dietary_pref="veg", is_opted_in=True),
                Resident(unit_no="B-204", name="Test User 2", phone="919888888888", dietary_pref="veg", is_opted_in=True),
            ])
            db.commit()

        # Add menu for the next 7 days (1 breakfast + 1 lunch + 1 dinner per day)
        today = date.today()
        for i in range(1, DAYS+1):
            d = today + timedelta(days=i)
            bi = (i-1) % len(BREAKFASTS)
            li = (i-1) % len(LUNCHES)
            di = (i-1) % len(DINNERS)
            rows = [
                MenuItem(menu_date=d, meal="breakfast", dish=BREAKFASTS[bi], is_veg=True, allergens=""),
                MenuItem(menu_date=d, meal="lunch",     dish=LUNCHES[li],    is_veg=True, allergens=""),
                MenuItem(menu_date=d, meal="dinner",    dish=DINNERS[di],    is_veg=True, allergens=""),
            ]
            for r in rows:
                # Avoid duplicates if you run this script twice
                exists = db.query(MenuItem).filter_by(menu_date=r.menu_date, meal=r.meal, dish=r.dish).first()
                if not exists:
                    db.add(r)
        db.commit()
        print("✅ Dummy residents + 7-day menu created.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
