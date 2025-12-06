#!/usr/bin/env bash

# ======================================================
# WeatherProject - Unified Launcher (Hybrid UI Edition)
# FastAPI (main.py)
# NiceGUI (ui/ui.py)
# Serial Reader (serial/serial_reader.py)
# ======================================================

set -e

echo "🚀 Starting WeatherProject..."

# ------------------------------------------------------
# 1) Determine base dir
# ------------------------------------------------------
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# ------------------------------------------------------
# 2) Activate virtual environment
# ------------------------------------------------------
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ venv not found! Create one with:"
    echo "python3 -m venv venv"
    exit 1
fi

# ------------------------------------------------------
# 2.5) Check for ML Model and Setup if missing
# ------------------------------------------------------
if [ ! -f "db/trained_weather_model.pkl" ]; then
    echo "⚠️ ML Model not found! Running setup..."
    python setup_ml.py
fi

# ------------------------------------------------------
# 3) Load environment variables
# ------------------------------------------------------
export API_BASE="http://localhost:8000"

if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create a .env file with your configuration:"
    echo "  1. Copy .env.example to .env"
    echo "  2. Edit .env with your API keys"
    echo ""
    echo "Example:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

if [ -f ".env" ]; then
    echo "🔐 Loading .env variables..."
    set -a  # Automatically export all variables
    source .env
    set +a  # Stop automatically exporting
fi

mkdir -p logs

# ------------------------------------------------------
# 4) Start Serial Reader
# ------------------------------------------------------
echo "📡 Starting sensor_serial/serial_reader.py..."
python sensor_serial/serial_reader.py > logs/serial.log 2>&1 &
SERIAL_PID=$!
echo "✔ serial_reader running (PID: $SERIAL_PID)"

# ------------------------------------------------------
# 5) Start FastAPI backend (main.py)
# ------------------------------------------------------
echo "⚙️ Starting FastAPI backend (main.py)..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!
echo "✔ FastAPI backend running (PID: $API_PID)"

# ------------------------------------------------------
# 6) Start NiceGUI UI (ui/ui.py)
# ------------------------------------------------------
echo "🌐 Starting NiceGUI UI (ui/ui.py)..."
python ui/ui.py > logs/ui.log 2>&1 &
UI_PID=$!
echo "✔ NiceGUI UI running (PID: $UI_PID)"

# ------------------------------------------------------
# 7) Final Message
# ------------------------------------------------------
echo ""
echo "🚀 WeatherProject is LIVE!"
echo "----------------------------------------"
echo "🔗 FastAPI Backend: http://localhost:8000"
echo "🔗 NiceGUI Frontend: http://localhost:8080"
echo "🛰️  Serial Reader: Running in background"
echo "----------------------------------------"
echo "📄 Logs located in ./logs/"
echo ""
echo "Press CTRL+C to stop everything"
echo ""

# ------------------------------------------------------
# 9) Handle shutdown
# ------------------------------------------------------
trap "echo '🛑 Stopping services...'; kill $SERIAL_PID $API_PID $UI_PID; exit 0" SIGINT

wait
