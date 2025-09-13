
import csv
from datetime import date, timedelta
from db import Base, engine, SessionLocal
from models import Resident, MenuItem

Base.metadata.create_all(bind=engine)

def seed_residents(db):
    with open("data/residents.csv") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if not db.query(Resident).filter_by(phone=row["phone"]).first():
                db.add(Resident(
                    unit_no=row["unit_no"],
                    name=row["name"],
                    phone=row["phone"],
                    dietary_pref=row.get("dietary_pref","veg"),
                    is_opted_in=row.get("is_opted_in","true").lower()=="true",
                    is_active=True
                ))
        db.commit()

def seed_menu(db):
    with open("data/menu.csv") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            db.add(MenuItem(
                menu_date=date.fromisoformat(row["menu_date"]),
                meal=row["meal"],
                dish=row["dish"],
                is_veg=row.get("is_veg","true").lower()=="true",
                allergens=row.get("allergens","")
            ))
        db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_residents(db)
        seed_menu(db)
        print("Seeded residents and menu.")
    finally:
        db.close()
