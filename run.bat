@echo off
REM Batch file to run Weather Prediction Pipeline on Windows

echo.
echo 🔧 Setting up environment...
echo.

REM Check if venv exists, if not create it
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt --quiet

echo.
echo Starting Weather Prediction Pipeline...
echo.

REM Run serial_reader.py
echo 1️⃣  Starting serial_reader.py...
start "" python serial_reader.py
timeout /t 2 /nobreak

REM Run train_ml_model.py
echo 2️⃣  Starting train_ml_model.py...
start "" python train_ml_model.py
timeout /t 2 /nobreak

REM Run streamlit app
echo 3️⃣  Starting Streamlit app...
start "" streamlit run main.py

echo.
echo ✅ All services started!
echo Press Ctrl+C in any window to stop each service individually,
echo or close all windows to stop everything...
echo.

pause
