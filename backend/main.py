from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import json
import asyncio
import math
import random
from datetime import datetime, timedelta

from database import SessionLocal, engine, Base
import models
import schemas
import auth
import seed_data


# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CargoBridge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ─── DB Dependency ───────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    user_id = auth.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        return None
    try:
        token = credentials.credentials
        user_id = auth.decode_token(token)
        if user_id:
            return db.query(models.User).filter(models.User.id == user_id).first()
    except:
        pass
    return None

# ─── Seed on startup ─────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_data.seed(db)
    finally:
        db.close()

# ─── AUTH ─────────────────────────────────────────────────────────────────────
@app.post("/signup", response_model=schemas.AuthResponse)
def signup(body: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(body.password)
    user = models.User(
        name=body.name,
        email=body.email,
        password_hash=hashed,
        role=body.role,
        company=body.company,
        phone=body.phone,
        license_number=body.license_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_token(user.id)
    return {"token": token, "user": schemas.UserOut.from_orm(user)}

@app.post("/login", response_model=schemas.AuthResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_token(user.id)
    return {"token": token, "user": schemas.UserOut.from_orm(user)}

@app.get("/me", response_model=schemas.UserOut)
def me(user=Depends(get_current_user)):
    return user

# ─── LISTINGS ────────────────────────────────────────────────────────────────
@app.get("/listings", response_model=List[schemas.ListingOut])
def get_listings(db: Session = Depends(get_db)):
    listings = db.query(models.ContainerListing).filter(
        models.ContainerListing.status == "active"
    ).order_by(models.ContainerListing.departure_date).all()
    return listings

@app.get("/listings/search", response_model=schemas.SearchResponse)
def search_listings(
    from_port: Optional[str] = None,
    to_port: Optional[str] = None,
    teu: Optional[int] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.ContainerListing).filter(models.ContainerListing.status == "active")
    if from_port and from_port != "Any":
        query = query.filter(models.ContainerListing.from_port.ilike(f"%{from_port}%"))
    if to_port and to_port != "Any":
        query = query.filter(models.ContainerListing.to_port.ilike(f"%{to_port}%"))
    if teu:
        query = query.filter(models.ContainerListing.available_teu >= teu)
    if days:
        cutoff = datetime.utcnow() + timedelta(days=days)
        query = query.filter(models.ContainerListing.departure_date <= cutoff)

    live_listings = query.order_by(models.ContainerListing.departure_date).all()

    # AI predictions
    predictions = generate_predictions(db, from_port, to_port, teu)

    return {
        "live": [schemas.ListingOut.from_orm(l) for l in live_listings],
        "predicted": predictions
    }

@app.get("/listings/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@app.post("/listings", response_model=schemas.ListingOut)
def create_listing(body: schemas.CreateListingRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "ff":
        raise HTTPException(status_code=403, detail="Only freight forwarders can create listings")
    listing = models.ContainerListing(
        forwarder_id=user.id,
        vessel_name=body.vessel_name,
        imo_number=body.imo_number,
        shipping_line=body.shipping_line,
        from_port=body.from_port,
        to_port=body.to_port,
        departure_date=body.departure_date,
        available_teu=body.available_teu,
        total_teu=body.total_teu,
        price_per_teu=body.price_per_teu,
        cargo_types=body.cargo_types,
        container_sizes=body.container_sizes,
        contact_email=body.contact_email,
        status="active",
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing

@app.put("/listings/{listing_id}", response_model=schemas.ListingOut)
def update_listing(listing_id: int, body: schemas.UpdateListingRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Not found")
    if listing.forwarder_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    for field, val in body.dict(exclude_none=True).items():
        setattr(listing, field, val)
    db.commit()
    db.refresh(listing)
    return listing

@app.get("/my-listings", response_model=List[schemas.ListingOut])
def my_listings(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "ff":
        raise HTTPException(status_code=403, detail="Only forwarders")
    return db.query(models.ContainerListing).filter(
        models.ContainerListing.forwarder_id == user.id
    ).order_by(models.ContainerListing.created_at.desc()).all()

# ─── BOOKINGS ────────────────────────────────────────────────────────────────
@app.post("/book", response_model=schemas.BookingOut)
def book_slot(body: schemas.BookingRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "sme":
        raise HTTPException(status_code=403, detail="Only SME users can book")
    listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == body.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.available_teu < body.teu_count:
        raise HTTPException(status_code=400, detail="Not enough TEU available")

    total = listing.price_per_teu * body.teu_count
    gst = round(total * 0.18)
    grand_total = total + gst
    ref = f"CB{int(datetime.utcnow().timestamp()) % 100000000:08d}"

    booking = models.Booking(
        reference=ref,
        sme_id=user.id,
        listing_id=body.listing_id,
        teu_count=body.teu_count,
        total_amount=grand_total,
        payment_method=body.payment_method,
        status="confirmed",
    )
    db.add(booking)

    payment = models.Payment(
        booking_reference=ref,
        amount=grand_total,
        method=body.payment_method,
        status="completed",
        transaction_id=f"TXN{ref}",
    )
    db.add(payment)

    listing.available_teu -= body.teu_count
    db.commit()
    db.refresh(booking)

    # Create booking request for forwarder
    req = models.BookingRequest(
        booking_id=booking.id,
        forwarder_id=listing.forwarder_id,
        sme_name=user.name,
        sme_company=user.company or "",
        teu_count=body.teu_count,
        total_amount=grand_total,
        note=body.note or "",
        status="pending",
    )
    db.add(req)
    db.commit()

    return booking

@app.get("/my-bookings", response_model=List[schemas.BookingOut])
def my_bookings(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "sme":
        raise HTTPException(status_code=403, detail="Only SME users")
    return db.query(models.Booking).filter(
        models.Booking.sme_id == user.id
    ).order_by(models.Booking.created_at.desc()).all()

# ─── FORWARDER ────────────────────────────────────────────────────────────────
@app.get("/requests", response_model=List[schemas.BookingRequestOut])
def get_requests(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "ff":
        raise HTTPException(status_code=403, detail="Only forwarders")
    return db.query(models.BookingRequest).filter(
        models.BookingRequest.forwarder_id == user.id
    ).order_by(models.BookingRequest.created_at.desc()).all()

@app.post("/approve/{request_id}", response_model=schemas.BookingRequestOut)
def approve_request(request_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(models.BookingRequest).filter(models.BookingRequest.id == request_id).first()
    if not req or req.forwarder_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "approved"
    booking = db.query(models.Booking).filter(models.Booking.id == req.booking_id).first()
    if booking:
        booking.status = "confirmed"
    db.commit()
    db.refresh(req)
    return req

@app.post("/reject/{request_id}", response_model=schemas.BookingRequestOut)
def reject_request(request_id: int, body: schemas.RejectRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(models.BookingRequest).filter(models.BookingRequest.id == request_id).first()
    if not req or req.forwarder_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "rejected"
    req.rejection_message = body.message
    booking = db.query(models.Booking).filter(models.Booking.id == req.booking_id).first()
    if booking:
        booking.status = "cancelled"
        # Restore TEU
        listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == booking.listing_id).first()
        if listing:
            listing.available_teu += booking.teu_count
    db.commit()
    db.refresh(req)
    return req

# ─── TRACKING ────────────────────────────────────────────────────────────────
PORT_COORDS = {
    "Mumbai JNPT": (18.9548, 72.9407),
    "Mumbai": (18.9548, 72.9407),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Mundra": (22.8394, 69.7152),
    "Cochin": (9.9312, 76.2673),
    "Dubai": (25.2048, 55.2708),
    "Singapore": (1.3521, 103.8198),
    "Rotterdam": (51.9225, 4.4792),
    "Hamburg": (53.5753, 10.0153),
    "Antwerp": (51.2213, 4.4051),
    "Colombo": (6.9271, 79.8612),
    "Felixstowe": (51.9567, 1.3518),
}

def interpolate(lat1, lon1, lat2, lon2, t):
    return lat1 + (lat2 - lat1) * t, lon1 + (lon2 - lon1) * t

@app.get("/track/{booking_id}")
def track_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == booking.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    from_coords = PORT_COORDS.get(listing.from_port, (18.9548, 72.9407))
    to_coords = PORT_COORDS.get(listing.to_port, (25.2048, 55.2708))

    dep = listing.departure_date
    now = datetime.utcnow()
    total_days = 14
    elapsed = max(0, (now - dep).total_seconds()) if now > dep else 0
    total_seconds = total_days * 86400
    t = min(1.0, elapsed / total_seconds)

    # Add some wave effect
    wave = math.sin(t * math.pi * 4) * 0.5
    cur_lat, cur_lon = interpolate(from_coords[0], from_coords[1], to_coords[0], to_coords[1], t)
    cur_lat += wave * 0.3
    cur_lon += wave * 0.1

    # Build route waypoints
    waypoints = []
    for i in range(11):
        pt = i / 10
        la, lo = interpolate(from_coords[0], from_coords[1], to_coords[0], to_coords[1], pt)
        waypoints.append({"lat": la, "lon": lo})

    return {
        "booking_id": booking_id,
        "reference": booking.reference,
        "vessel_name": listing.vessel_name,
        "from_port": listing.from_port,
        "to_port": listing.to_port,
        "from_coords": {"lat": from_coords[0], "lon": from_coords[1]},
        "to_coords": {"lat": to_coords[0], "lon": to_coords[1]},
        "current": {"lat": cur_lat, "lon": cur_lon},
        "progress": round(t * 100, 1),
        "speed_knots": round(14 + random.uniform(-2, 2), 1),
        "heading": round(math.degrees(math.atan2(to_coords[1] - from_coords[1], to_coords[0] - from_coords[0])), 1),
        "eta_days": round((1 - t) * total_days, 1),
        "waypoints": waypoints,
        "status": "at_sea" if 0 < t < 1 else ("at_origin" if t == 0 else "arrived"),
        "departure_date": dep.isoformat(),
    }

# ─── AI PREDICTIONS ──────────────────────────────────────────────────────────
def generate_predictions(db, from_port=None, to_port=None, teu=None):
    routes = [
        ("Mumbai JNPT", "Dubai", 7),
        ("Mumbai JNPT", "Singapore", 14),
        ("Chennai", "Rotterdam", 21),
        ("Mundra", "Hamburg", 22),
        ("Kolkata", "Felixstowe", 25),
    ]
    predictions = []
    for origin, dest, base_days in routes:
        if from_port and from_port != "Any" and from_port.lower() not in origin.lower():
            continue
        if to_port and to_port != "Any" and to_port.lower() not in dest.lower():
            continue

        score = random.uniform(0.65, 0.98)
        predicted_teu = random.randint(80, 600)
        if teu and predicted_teu < teu:
            predicted_teu = teu + random.randint(10, 100)

        dep_date = datetime.utcnow() + timedelta(days=base_days + random.randint(-2, 5))
        predictions.append({
            "id": f"pred_{origin[:3]}_{dest[:3]}_{random.randint(100, 999)}",
            "is_predicted": True,
            "vessel_name": f"AI Predicted Slot — {origin[:3]}/{dest[:3]}",
            "from_port": origin,
            "to_port": dest,
            "departure_date": dep_date.isoformat(),
            "available_teu": predicted_teu,
            "price_per_teu": round(random.uniform(28000, 72000) / 1000) * 1000,
            "confidence": round(score, 2),
            "ai_score": round(score * 100, 1),
            "shipping_line": "AI Estimate",
            "co2_saved_tonnes": round(predicted_teu * 2.3, 1),
        })
    predictions.sort(key=lambda x: x["confidence"], reverse=True)
    return predictions

@app.get("/predictions")
def predictions(from_port: Optional[str] = None, to_port: Optional[str] = None, teu: Optional[int] = None, db: Session = Depends(get_db)):
    return generate_predictions(db, from_port, to_port, teu)

# ─── CO2 CALCULATOR ──────────────────────────────────────────────────────────
@app.get("/co2")
def co2_calculator(teu: int = 20, from_port: str = "Mumbai JNPT", to_port: str = "Dubai"):
    distances = {
        ("Mumbai JNPT", "Dubai"): 2000,
        ("Mumbai JNPT", "Singapore"): 2700,
        ("Chennai", "Rotterdam"): 8800,
        ("Mundra", "Hamburg"): 9500,
        ("Kolkata", "Felixstowe"): 8400,
    }
    dist = distances.get((from_port, to_port), distances.get((to_port, from_port), 5000))
    co2_per_teu_km = 0.0135  # kg CO2 per TEU per km
    co2_saved = round(teu * dist * co2_per_teu_km / 1000, 2)  # tonnes
    trees = round(co2_saved * 45)
    return {
        "teu": teu,
        "route": f"{from_port} → {to_port}",
        "distance_nm": dist,
        "co2_saved_tonnes": co2_saved,
        "equivalent_trees": trees,
        "equivalent_cars_off_road": round(co2_saved / 2.3, 1),
    }

# ─── STATS ───────────────────────────────────────────────────────────────────
@app.get("/stats")
def platform_stats(db: Session = Depends(get_db)):
    total_listings = db.query(models.ContainerListing).count()
    total_bookings = db.query(models.Booking).filter(models.Booking.status == "confirmed").count()
    total_teu = db.query(models.Booking).with_entities(
        models.Booking.teu_count
    ).filter(models.Booking.status == "confirmed").all()
    teu_sum = sum(t[0] for t in total_teu)
    return {
        "total_listings": total_listings,
        "confirmed_bookings": total_bookings,
        "total_teu_matched": teu_sum,
        "smes_active": db.query(models.User).filter(models.User.role == "sme").count(),
        "forwarders": db.query(models.User).filter(models.User.role == "ff").count(),
    }

# ─── WEBSOCKET TRACKING ──────────────────────────────────────────────────────
@app.websocket("/ws/track/{booking_id}")
async def websocket_track(websocket: WebSocket, booking_id: int):
    await websocket.accept()
    db = SessionLocal()
    try:
        for _ in range(300):  # 5 min max
            booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
            if not booking:
                await websocket.send_json({"error": "Booking not found"})
                break
            listing = db.query(models.ContainerListing).filter(models.ContainerListing.id == booking.listing_id).first()
            if not listing:
                break
            from_c = PORT_COORDS.get(listing.from_port, (18.9548, 72.9407))
            to_c = PORT_COORDS.get(listing.to_port, (25.2048, 55.2708))
            dep = listing.departure_date
            now = datetime.utcnow()
            elapsed = max(0, (now - dep).total_seconds())
            total_s = 14 * 86400
            t = min(1.0, elapsed / total_s)
            wave = math.sin(t * math.pi * 4 + random.uniform(0, 0.1)) * 0.5
            la, lo = interpolate(from_c[0], from_c[1], to_c[0], to_c[1], t)
            la += wave * 0.3 + random.uniform(-0.02, 0.02)
            lo += wave * 0.1 + random.uniform(-0.02, 0.02)
            await websocket.send_json({
                "lat": la, "lon": lo,
                "progress": round(t * 100, 1),
                "speed": round(14 + random.uniform(-2, 2), 1),
                "eta_days": round((1 - t) * 14, 1),
                "timestamp": now.isoformat(),
            })
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
