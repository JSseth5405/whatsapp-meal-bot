
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Resident(Base):
    __tablename__ = "residents"
    id = Column(Integer, primary_key=True)
    unit_no = Column(String, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)  # WhatsApp MSISDN in international format without +
    is_opted_in = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    dietary_pref = Column(String, default="veg")  # veg/non-veg/mixed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    menu_date = Column(Date, index=True)  # date the meal is served
    meal = Column(String, index=True)     # breakfast/lunch/dinner
    dish = Column(String)
    is_veg = Column(Boolean, default=True)
    allergens = Column(String, default="")  # comma-separated

    __table_args__ = (UniqueConstraint("menu_date", "meal", "dish", name="uq_menuitem"),)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id"))
    menu_date = Column(Date, index=True)
    meal = Column(String, index=True)  # breakfast/lunch/dinner
    qty = Column(Integer, default=1)
    status = Column(String, default="booked")  # booked/cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resident = relationship("Resident", backref="bookings")

class SessionState(Base):
    __tablename__ = "session_state"
    id = Column(Integer, primary_key=True)
    phone = Column(String, index=True)
    state = Column(String, default="idle")
    context = Column(String, default="{}")  # JSON text for small state
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
