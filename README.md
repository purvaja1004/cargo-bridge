# CargoBridge

CargoBridge is a web-based freight-booking platform that helps small and medium enterprises (SMEs) discover and book available shipping-container slots offered by freight forwarders.

It provides separate SME and freight-forwarder workflows for slot management, booking, payment records, CO₂-savings estimates, and vessel-tracking simulation.

## Features

- SME and freight-forwarder user roles with JWT-based authentication
- Freight forwarders can create, update, and manage container-slot listings
- SMEs can search listings by origin, destination, TEU capacity, and departure window
- Booking workflow with capacity validation, booking references, and payment records
- Forwarder approval and rejection workflow for booking requests
- Route-based availability predictions and estimated CO₂ savings
- Vessel-tracking interface with route waypoints and WebSocket updates
- Interactive maps powered by Leaflet and OpenStreetMap

## Tech Stack

**Backend**

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication
- WebSockets

**Frontend**

- HTML, CSS, and JavaScript
- Leaflet
- OpenStreetMap

## Project Structure

```text
cargobridge/
├── backend/
│   ├── main.py           ← FastAPI server and API routes
│   ├── models.py         ← SQLAlchemy database tables
│   ├── schemas.py        ← Pydantic request and response schemas
│   ├── auth.py           ← JWT tokens and password hashing
│   ├── seed_data.py      ← Demo vessels and users
│   ├── database.py       ← SQLite database connection
│   └── requirements.txt  ← Python dependencies
├── frontend/
│   ├── index.html        ← Landing page and authentication modal
│   ├── api.js            ← Shared API client
│   ├── translations.json ← English and Hindi strings
│   └── pages/
│       ├── dashboard.html  ← SME dashboard
│       └── forwarder.html  ← Freight-forwarder portal
├── START_BACKEND.bat     ← Windows startup script
├── start_backend.sh      ← Mac/Linux startup script
└── README.md
```

## Instructions for Opening the Website

### (if backend is running properly that is if virtual environment and all dependencies are already installed skip to run backend step)

### 1. Create Virtual Environment:
  python -m venv venv

Activate it:
  venv\Scripts\activate

### 2. Upgrade pip: 
  pip install --upgrade pip setuptools wheel

### 3. Install Dependencies (No Rust Issues):
  pip install fastapi==0.109.2 uvicorn==0.27.1 python-multipart PyJWT passlib[bcrypt]

If installation fails, run:
  pip install --only-binary=:all: fastapi uvicorn

### 4. Fix JWT Error:
  pip install PyJWT

### 5. Run Backend Server
   
  Go to backend folder:
  cd cargobridge/backend

Run START_BACKEND file

Then open index.html in live server

Some ids which we have created 
#### For SME-

  riabogawat203@gmail.com
  Password- Ria@2006

#### For FF-

  arjun@mehtafreight.com
  Password- demo1234
 

## MVP:

1. SME-first

2. Dual-engine: Live forwarder listings + AI predictions

3. Carbon tracking: CO₂ savings per booking  
