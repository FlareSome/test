# Weather Prediction System

A comprehensive IoT-based weather prediction system that collects real-time sensor data, trains machine learning models, and provides forecasts through an interactive Streamlit dashboard.

## 🌟 Features

- **Real-time Data Collection**: Serial reader for IoT weather station sensors
- **Machine Learning**: Random Forest model for temperature prediction
- **Data Processing**: ETL pipeline for weather data
- **Interactive Dashboard**: Streamlit-based UI for visualization and forecasting
- **Gemini AI Integration**: Advanced weather forecasting with Google's Gemini API
- **Cross-platform**: Windows (.bat) and Linux/Mac (.sh) support

## 📋 Project Structure

```
app/
├── main.py                 # Streamlit dashboard application
├── serial_reader.py        # IoT sensor data collection
├── train_ml_model.py       # ML model training pipeline
├── data_handler.py         # Data processing utilities
├── iot_data_processor.py   # IoT data processing
├── gemini_forecast.py      # Gemini API integration
├── weather_station.ino     # Arduino firmware
├── assets/                 # UI themes (light/dark)
├── utils/                  # Utility modules
├── requirements.txt        # Python dependencies
├── run.sh                  # Linux/Mac startup script
├── run.bat                 # Windows startup script
└── README.md               # This file
```

## 🛠️ Tech Stack

- **Backend**: Python 3.x
- **Data Science**: Pandas, NumPy, Scikit-learn
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Hardware**: Arduino (IoT Weather Station)
- **API**: Google Gemini API
- **Database**: CSV-based (expandable to SQL)

## 📦 Dependencies

- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning
- `joblib` - Model persistence
- `pyserial` - Serial communication
- `plotly` - Interactive visualizations
- `adafruit-circuitpython-bmp280` - Sensor library

See `requirements.txt` for complete list.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
run.bat
```

### Option 2: Manual Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run components individually:**
   ```bash
   python serial_reader.py    # Start sensor reader
   python train_ml_model.py   # Train ML model
   streamlit run main.py      # Start dashboard
   ```

## 📡 Hardware Setup

### Arduino Weather Station
- Upload `weather_station.ino` to your Arduino board
- Connect BMP280 sensor for temperature, humidity, and pressure readings
- Configure serial port in `serial_reader.py`

### Supported Sensors
- **Temperature**: BMP280
- **Humidity**: BMP280
- **Pressure**: BMP280
- **Rainfall**: GPIO-based rain gauge

## 🤖 Machine Learning

The system uses a **Random Forest Regressor** to predict temperature based on:
- Historical temperature
- Humidity percentage
- Atmospheric pressure
- Rainfall
- Time features (hour, day of year)

### Training
```bash
python train_ml_model.py
```

Model is saved to `ml_weather_model.pkl` for later predictions.

## 📊 Data Files

- `raw_data.csv` - Raw sensor data
- `forecast_log.csv` - Prediction history
- `ml_weather_model.pkl` - Trained ML model (generated)

## 🔐 Security Best Practices

- **API Keys**: Store in environment variables (see `QUICK_SETUP.md`)
- **.gitignore**: Sensitive files excluded from version control
- **Virtual Environment**: Isolates dependencies
- **No hardcoded secrets**: Use `.env` files (not committed)

## 🌐 Environment Variables

Create a `.env` file (not committed to git):
```
GEMINI_API_KEY=your_api_key_here
SERIAL_PORT=/dev/ttyUSB0  # Linux/Mac or COM3 for Windows
SERIAL_BAUD=9600
```

## 🐛 Troubleshooting

### Virtual environment not activating
```bash
python3 -m venv venv --clear
```

### Serial port not found
- Check Arduino connection: `ls /dev/tty*` (Linux/Mac)
- Check Device Manager (Windows)
- Update `SERIAL_PORT` in `.env`

### Streamlit not starting
```bash
pip install --upgrade streamlit
```

### Model training fails
- Ensure `raw_data.csv` exists and has valid data
- Check column names match the script expectations

## 📈 Usage Workflow

1. **Data Collection**: `serial_reader.py` reads sensor data continuously
2. **Data Processing**: `data_handler.py` cleans and prepares data
3. **Model Training**: `train_ml_model.py` trains on collected data
4. **Forecasting**: `gemini_forecast.py` generates AI predictions
5. **Dashboard**: `main.py` visualizes everything in Streamlit

## 🔄 Continuous Operation

The system is designed to run continuously:
- Sensor reader collects data 24/7
- Model retrains periodically (can be scheduled)
- Dashboard always available for monitoring
- Forecasts updated in real-time

## 📝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Add your license here]

## 👤 Author

FlareSome

## 📞 Support

For issues or questions, open an issue on GitHub.

---

**Last Updated**: November 2025
