#!/bin/bash
echo "============================================"
echo "  CargoBridge - Starting Backend Server"
echo "============================================"
echo ""

cd "$(dirname "$0")/backend"

echo "[1/3] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Install from python.org"
    exit 1
fi

echo "[2/3] Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo "[3/3] Starting CargoBridge API server..."
echo ""
echo " Backend running at: http://localhost:8000"
echo " API docs at:        http://localhost:8000/docs"
echo ""
echo " Demo accounts:"
echo "   SME:       ria@sharmaexports.com  / demo1234"
echo "   Forwarder: arjun@mehtafreight.com / demo1234"
echo ""
echo " Open frontend/index.html in your browser!"
echo ""
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
