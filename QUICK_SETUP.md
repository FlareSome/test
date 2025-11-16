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
3. ✅ Start the sensor reader
4. ✅ Train the ML model
5. ✅ Launch the Streamlit dashboard

---

## 📋 Manual Setup (If Needed)

### Step 1: Clone/Navigate to Project
```bash
cd app
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

Create a `.env` file in the project root:
```bash
# .env file (do NOT commit this!)
GEMINI_API_KEY=your_gemini_api_key
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
python serial_reader.py
```

Terminal 2 - Model Training:
```bash
python train_ml_model.py
```

Terminal 3 - Dashboard:
```bash
streamlit run main.py
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

### Gemini API Setup

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

### Test Streamlit
```bash
streamlit hello
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

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
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

### Issue: Streamlit port already in use
**Solution:** Change port:
```bash
streamlit run main.py --server.port 8502
```

---

## 📂 Expected Data Files

After first run, you should see:
- ✅ `raw_data.csv` - Sensor data
- ✅ `ml_weather_model.pkl` - Trained model
- ✅ `forecast_log.csv` - Predictions history
- ✅ `venv/` - Virtual environment

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
1. 🌐 Open **Streamlit Dashboard**: http://localhost:8501
2. 📡 **Sensor Reader** collecting data in background
3. 🤖 **ML Model** continuously training
4. 📊 **Predictions** updating in real-time

---

## 📚 Next Steps

- Read `README.md` for full documentation
- Check individual Python files for detailed comments
- Monitor `forecast_log.csv` for prediction history
- Customize themes in `assets/` folder

---

**Happy Weather Predicting! 🌤️**
