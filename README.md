# DPWH005

Instructions for opening website 

(if backend is running properly that is if virtual environment and all dependencies are already installed skip to run backend step)

1. Create Virtual Environment:
  python -m venv venv

Activate it:
  venv\Scripts\activate

2. Upgrade pip: 
  pip install --upgrade pip setuptools wheel

3. Install Dependencies (No Rust Issues):
  pip install fastapi==0.109.2 uvicorn==0.27.1 python-multipart PyJWT passlib[bcrypt]

If installation fails, run:
  pip install --only-binary=:all: fastapi uvicorn

4. Fix JWT Error:
  pip install PyJWT

5. Run Backend Server
   
  Go to backend folder:
  cd cargobridge/backend

Run START_BACKEND file

Then open index.html in live server

Some ids which we have created 
For SME-

  riabogawat203@gmail.com
  Password- Ria@2006

For FF-

  arjun@mehtafreight.com
  Password- demo1234


**MVP:**

1. SME-first

2. Dual-engine: Live forwarder listings + AI predictions

3. Carbon tracking: CO₂ savings per booking  
