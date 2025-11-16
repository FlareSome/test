#!/bin/bash

# Trap Ctrl+C to clean up all background processes
trap 'echo "Shutting down..."; kill $(jobs -p) 2>/dev/null; exit 0' SIGINT

echo "🔧 Setting up environment..."
echo ""

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt --quiet

echo ""
echo "Starting Weather Prediction Pipeline..."
echo ""

# Run serial_reader.py
echo "1️⃣  Starting serial_reader.py..."
python serial_reader.py &
SERIAL_PID=$!
sleep 2

# Run train_ml_model.py
echo "2️⃣  Starting train_ml_model.py..."
python train_ml_model.py &
TRAIN_PID=$!
sleep 2

# Run streamlit app
echo "3️⃣  Starting Streamlit app..."
streamlit run main.py &
STREAMLIT_PID=$!

echo ""
echo "✅ All services started!"
echo "Press Ctrl+C to stop everything..."
echo ""

# Wait for all background processes
wait
