# ⚡ Quick Setup Guide

Get your Weather Prediction System up and running in minutes!

## 🎯 Prerequisites

- **Python 3.8+** installed
- **Git** installed
- **Arduino IDE** (optional, for firmware upload)
- **pip** package manager

## 🚀 One-Command Setup

### Linux / macOS
```bash
chmod +x run.sh && ./run.sh
```

### Windows
```bash
run.bat
```

That's it! The script will:
1. ✅ Create a virtual environment
2. ✅ Install all dependencies
3. ✅ Start the sensor reader (background)
4. ✅ Start the FastAPI backend (port 8000)
5. ✅ Launch the NiceGUI dashboard (port 8080)

---

## 📋 Manual Setup (If Needed)

### Step 1: Clone/Navigate to Project
```bash
cd Weather_Prediction
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Copy the example file and edit with your values:
```bash
cp .env.example .env
```

Then edit `.env` with your actual configuration:
```bash
# .env file (do NOT commit this!)
WEATHERAPI_KEY=your_weatherapi_key_here
CITY_NAME=New Town, West Bengal
API_BASE=http://localhost:8000
SERIAL_PORT=/dev/ttyUSB0  # Linux/Mac: check with ls /dev/tty*
SERIAL_BAUD=9600
```

**For Windows, SERIAL_PORT might be:** `COM3`, `COM4`, etc.

### Step 6: Upload Arduino Firmware (First Time Only)

1. Open Arduino IDE
2. Load `weather_station.ino`
3. Connect your Arduino board
4. Upload the sketch
5. Note the serial port (shown in Arduino IDE)

### Step 7: Run the System

**Option A: All-in-One**
```bash
./run.sh  # Linux/Mac
run.bat   # Windows
```

**Option B: Individual Components**

Terminal 1 - Sensor Reader:
```bash
python serial/serial_reader.py
```

Terminal 2 - FastAPI Backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Terminal 3 - NiceGUI Dashboard:
```bash
python ui/ui.py
```

---

## 🔧 Configuration

### Serial Port Detection

**Linux/macOS:**
```bash
ls /dev/tty*
# Look for /dev/ttyUSB0, /dev/ttyACM0, or /dev/cu.usbserial*
```

**Windows:**
- Open Device Manager
- Look under "Ports (COM & LPT)"
- Note the COM port (e.g., COM3)

### Baud Rate
Default: `9600` - Match this with your Arduino firmware!

### WeatherAPI Setup

1. Go to [WeatherAPI](https://www.weatherapi.com/)
2. Sign up for a free account
3. Get your API key
4. Add to `.env` file:
   ```bash
   WEATHERAPI_KEY=your_key_here
   ```

### Gemini API Setup (Optional)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env` file:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```

---

## 📊 Verify Installation

### Check Python Version
```bash
python --version  # Should be 3.8+
```

### Check Pip
```bash
pip list
```

### Test Data Loading
```bash
python -c "import pandas; print('✅ Pandas OK')"
```

### Test NiceGUI
```bash
python -c "import nicegui; print('✅ NiceGUI OK')"
```

---

## 🛑 Stopping the Application

### Linux/macOS
- Press `Ctrl+C` once to gracefully stop all services

### Windows
- Close the command prompt window or
- Press `Ctrl+C` in each window

---

## ⚠️ Common Issues & Solutions

### Issue: "python: command not found"
**Solution:** Use `python3` instead, or add Python to PATH

### Issue: "pip: command not found"
**Solution:** Use `python -m pip install` instead

### Issue: "ModuleNotFoundError: No module named 'nicegui'"
**Solution:** Ensure venv is activated and run:
```bash
pip install -r requirements.txt
```

### Issue: Serial port permission denied (Linux)
**Solution:** Add your user to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Then restart your terminal
```

### Issue: Arduino not detected
**Solution:**
1. Install CH340 drivers if needed
2. Check USB cable
3. Verify Arduino firmware uploaded
4. Update SERIAL_PORT in `.env`

### Issue: Model training fails with "CSV not found"
**Solution:** Ensure `raw_data.csv` exists in the project root with proper data

### Issue: Port already in use
**Solution:** Change port:
```bash
# For NiceGUI
python ui/ui.py --port 8081

# For FastAPI
uvicorn main:app --port 8001
```

---

## 📂 Expected Files After Setup

After cloning and first run, you should have:
- ✅ `.env` - Your configuration (copied from `.env.example`)
- ✅ `venv/` - Virtual environment
- ✅ `weather_data.db` - SQLite database (auto-created)
- ✅ `logs/` - Log files directory
- ✅ `data/` - Data files (CSV, JSON)

---

## 🔒 Security Checklist

- [ ] Created `.env` file with API keys
- [ ] `.gitignore` excludes `.env`
- [ ] `.gitignore` excludes `venv/`
- [ ] `.gitignore` excludes `__pycache__/`
- [ ] No API keys in source code
- [ ] Virtual environment activated before installing packages

---

## ✅ You're Ready!

Once everything is running:
1. 🌐 **FastAPI Backend**: http://localhost:8000
2. 🖥️ **NiceGUI Dashboard**: http://localhost:8080
3. 📡 **Sensor Reader** collecting data in background
4. 🤖 **ML Model** making predictions
5. 📊 **Charts** updating in real-time

---

## 📚 Next Steps

- Read `README.md` for full documentation
- Check individual Python files for detailed comments
- Monitor `forecast_log.csv` for prediction history
- Customize themes in `assets/` folder

---

**Happy Weather Predicting! 🌤️**
