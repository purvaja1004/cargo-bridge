from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'sme' or 'ff'
    company = Column(String)
    phone = Column(String)
    license_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("ContainerListing", back_populates="forwarder")
    bookings = relationship("Booking", back_populates="sme")


class ContainerListing(Base):
    __tablename__ = "container_listings"
    id = Column(Integer, primary_key=True, index=True)
    forwarder_id = Column(Integer, ForeignKey("users.id"))
    vessel_name = Column(String, nullable=False)
    imo_number = Column(String)
    shipping_line = Column(String)
    from_port = Column(String, nullable=False)
    to_port = Column(String, nullable=False)
    departure_date = Column(DateTime, nullable=False)
    available_teu = Column(Integer, nullable=False)
    total_teu = Column(Integer)
    price_per_teu = Column(Float, nullable=False)
    cargo_types = Column(String, default="General")
    container_sizes = Column(String, default="20ft, 40ft")
    contact_email = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    forwarder = relationship("User", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True)
    sme_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("container_listings.id"))
    teu_count = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, default="upi")
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

    sme = relationship("User", back_populates="bookings")
    listing = relationship("ContainerListing", back_populates="bookings")
    request = relationship("BookingRequest", back_populates="booking", uselist=False)


class BookingRequest(Base):
    __tablename__ = "booking_requests"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    forwarder_id = Column(Integer, ForeignKey("users.id"))
    sme_name = Column(String)
    sme_company = Column(String)
    teu_count = Column(Integer)
    total_amount = Column(Float)
    note = Column(Text, default="")
    status = Column(String, default="pending")  # pending, approved, rejected
    rejection_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="request")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String, index=True)
    amount = Column(Float)
    method = Column(String)
    status = Column(String, default="completed")
    transaction_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
