from datetime import datetime, timedelta
import models
import auth


def seed(db):
    # Check if already seeded
    if db.query(models.User).count() > 0:
        return

    print("🌱 Seeding database...")

    # Create demo users
    ff_user = models.User(
        name="Arjun Mehta",
        email="arjun@mehtafreight.com",
        password_hash=auth.hash_password("demo1234"),
        role="ff",
        company="Mehta Freight Forwarders Pvt Ltd",
        phone="+91 98765 43210",
        license_number="FFFAI-MUM-2024-1234",
    )
    sme_user = models.User(
        name="Ria Sharma",
        email="ria@sharmaexports.com",
        password_hash=auth.hash_password("demo1234"),
        role="sme",
        company="Sharma Exports Pvt Ltd",
        phone="+91 87654 32109",
    )
    ff2 = models.User(
        name="Priya Nair",
        email="priya@oceanfreight.com",
        password_hash=auth.hash_password("demo1234"),
        role="ff",
        company="Ocean Freight Solutions",
        phone="+91 76543 21098",
        license_number="FFFAI-CHN-2024-5678",
    )
    db.add_all([ff_user, sme_user, ff2])
    db.commit()
    db.refresh(ff_user)
    db.refresh(ff2)

    now = datetime.utcnow()

    # 10 demo vessels / listings
    listings_data = [
        {
            "vessel_name": "MSC Pragya",
            "imo_number": "IMO9876543",
            "shipping_line": "MSC",
            "from_port": "Mumbai JNPT",
            "to_port": "Dubai",
            "departure_date": now + timedelta(days=5),
            "available_teu": 320,
            "total_teu": 800,
            "price_per_teu": 42000,
            "cargo_types": "General, Reefer",
            "container_sizes": "20ft, 40ft, 40ft HC",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
        {
            "vessel_name": "Maersk Kolkata",
            "imo_number": "IMO9765432",
            "shipping_line": "Maersk",
            "from_port": "Mumbai JNPT",
            "to_port": "Singapore",
            "departure_date": now + timedelta(days=8),
            "available_teu": 550,
            "total_teu": 1200,
            "price_per_teu": 38500,
            "cargo_types": "General",
            "container_sizes": "20ft, 40ft",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
        {
            "vessel_name": "COSCO Chennai",
            "imo_number": "IMO9654321",
            "shipping_line": "COSCO",
            "from_port": "Chennai",
            "to_port": "Rotterdam",
            "departure_date": now + timedelta(days=12),
            "available_teu": 890,
            "total_teu": 2000,
            "price_per_teu": 68000,
            "cargo_types": "General, Hazmat",
            "container_sizes": "20ft, 40ft, 40ft HC, 45ft HC",
            "contact_email": "priya@oceanfreight.com",
            "forwarder_id": ff2.id,
        },
        {
            "vessel_name": "Evergreen Mumbai",
            "imo_number": "IMO9543210",
            "shipping_line": "Evergreen",
            "from_port": "Mundra",
            "to_port": "Hamburg",
            "departure_date": now + timedelta(days=9),
            "available_teu": 1050,
            "total_teu": 2500,
            "price_per_teu": 71500,
            "cargo_types": "General, Reefer",
            "container_sizes": "20ft, 40ft, 40ft HC",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
        {
            "vessel_name": "PIL Andaman",
            "imo_number": "IMO9432109",
            "shipping_line": "PIL",
            "from_port": "Kolkata",
            "to_port": "Felixstowe",
            "departure_date": now + timedelta(days=14),
            "available_teu": 240,
            "total_teu": 600,
            "price_per_teu": 65000,
            "cargo_types": "General",
            "container_sizes": "20ft, 40ft",
            "contact_email": "priya@oceanfreight.com",
            "forwarder_id": ff2.id,
        },
        {
            "vessel_name": "CMA CGM Gujarat",
            "imo_number": "IMO9321098",
            "shipping_line": "CMA CGM",
            "from_port": "Mumbai JNPT",
            "to_port": "Rotterdam",
            "departure_date": now + timedelta(days=18),
            "available_teu": 780,
            "total_teu": 1800,
            "price_per_teu": 72000,
            "cargo_types": "General, Reefer, Hazmat",
            "container_sizes": "20ft, 40ft, 40ft HC, 45ft HC",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
        {
            "vessel_name": "Hapag Chennai Star",
            "imo_number": "IMO9210987",
            "shipping_line": "Hapag-Lloyd",
            "from_port": "Chennai",
            "to_port": "Singapore",
            "departure_date": now + timedelta(days=4),
            "available_teu": 390,
            "total_teu": 900,
            "price_per_teu": 36000,
            "cargo_types": "General",
            "container_sizes": "20ft, 40ft",
            "contact_email": "priya@oceanfreight.com",
            "forwarder_id": ff2.id,
        },
        {
            "vessel_name": "ONE Mundra Express",
            "imo_number": "IMO9109876",
            "shipping_line": "ONE",
            "from_port": "Mundra",
            "to_port": "Dubai",
            "departure_date": now + timedelta(days=3),
            "available_teu": 160,
            "total_teu": 400,
            "price_per_teu": 39000,
            "cargo_types": "General, Reefer",
            "container_sizes": "20ft, 40ft",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
        {
            "vessel_name": "Yang Ming Deccan",
            "imo_number": "IMO9098765",
            "shipping_line": "Yang Ming",
            "from_port": "Cochin",
            "to_port": "Colombo",
            "departure_date": now + timedelta(days=2),
            "available_teu": 85,
            "total_teu": 200,
            "price_per_teu": 18000,
            "cargo_types": "General",
            "container_sizes": "20ft, 40ft",
            "contact_email": "priya@oceanfreight.com",
            "forwarder_id": ff2.id,
        },
        {
            "vessel_name": "MSC Bay of Bengal",
            "imo_number": "IMO9087654",
            "shipping_line": "MSC",
            "from_port": "Kolkata",
            "to_port": "Singapore",
            "departure_date": now + timedelta(days=11),
            "available_teu": 620,
            "total_teu": 1400,
            "price_per_teu": 41000,
            "cargo_types": "General, Hazmat",
            "container_sizes": "20ft, 40ft, 40ft HC",
            "contact_email": "arjun@mehtafreight.com",
            "forwarder_id": ff_user.id,
        },
    ]

    for ld in listings_data:
        listing = models.ContainerListing(**ld)
        db.add(listing)
    db.commit()

    print("✅ Seed complete: 3 users, 10 listings created")
    print("📧 Demo accounts:")
    print("   SME:      ria@sharmaexports.com / demo1234")
    print("   Forwarder: arjun@mehtafreight.com / demo1234")
