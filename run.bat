@echo off
REM ======================================================
REM Weather Prediction System - Windows Launcher
REM FastAPI Backend + NiceGUI Dashboard + Serial Reader
REM ======================================================

echo.
echo 🌤️  Weather Prediction System - Starting...
echo.

REM ------------------------------------------------------
REM 1) Check if venv exists, if not create it
REM ------------------------------------------------------
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM ------------------------------------------------------
REM 2) Activate virtual environment
REM ------------------------------------------------------
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM ------------------------------------------------------
REM 3) Install/update requirements
REM ------------------------------------------------------
echo 📥 Installing/updating requirements...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️  Warning: Some packages may have failed to install
)

REM ------------------------------------------------------
REM 4) Check for .env file
REM ------------------------------------------------------
if not exist ".env" (
    echo.
    echo ⚠️  WARNING: .env file not found!
    echo.
    echo Please create a .env file with your configuration:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env with your API keys
    echo.
    echo Example:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------
REM 5) Create logs directory
REM ------------------------------------------------------
if not exist "logs" mkdir logs

echo.
echo 🚀 Starting Weather Prediction System...
echo.

REM ------------------------------------------------------
REM 6) Start serial reader in background (optional)
REM ------------------------------------------------------
echo 1️⃣  Starting serial reader (IoT sensor)...
start /B python serial\serial_reader.py > logs\serial.log 2>&1

REM Give it a moment to start
timeout /t 2 /nobreak > nul

REM ------------------------------------------------------
REM 7) Start FastAPI backend in background
REM ------------------------------------------------------
echo 2️⃣  Starting FastAPI backend (port 8000)...
start /B uvicorn main:app --host 0.0.0.0 --port 8000 > logs\api.log 2>&1

REM Give it a moment to start
timeout /t 3 /nobreak > nul

REM ------------------------------------------------------
REM 8) Start NiceGUI dashboard (foreground)
REM ------------------------------------------------------
echo 3️⃣  Starting NiceGUI dashboard (port 8080)...
echo.
echo ========================================
echo 🚀 Weather Prediction System is LIVE!
echo ========================================
echo 🔗 FastAPI Backend:  http://localhost:8000
echo 🔗 NiceGUI Dashboard: http://localhost:8080
echo 🛰️  Serial Reader:    Running in background
echo ========================================
echo 📄 Logs located in .\logs\
echo.
echo Press CTRL+C to stop all services
echo.

python ui\ui.py

REM ------------------------------------------------------
REM 9) Cleanup message
REM ------------------------------------------------------
echo.
echo ✅ System stopped.
echo.

pause
