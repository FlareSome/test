import serial
import serial.tools.list_ports
import json
from datetime import datetime, timezone
import time
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.db import init_db, insert_reading

# Ensure DB exists
init_db()

DEFAULT_BAUD = int(os.getenv("SERIAL_BAUD", "115200"))
ENV_PORT = os.getenv("SERIAL_PORT", "").strip()

def find_port():
    # 1) Use env override if provided
    if ENV_PORT:
        return ENV_PORT

    # 2) Auto-detect common Arduino/USB serial names
    for p in serial.tools.list_ports.comports():
        d = (p.device or "").lower()
        desc = (p.description or "").lower()
        if any(x in d for x in ("usb", "acm", "ttyusb", "ttyacm", "com")) or "arduino" in desc:
            return p.device
    return None

def safe_float(v, default=None):
    try:
        return float(v)
    except:
        return default

def run_serial_loop():
    print(f"Starting Serial Reader Service...")
    
    while True:
        port = find_port()
        
        if not port:
            print("⚠️  No Arduino found. Retrying in 2s...")
            time.sleep(2)
            continue
            
        print(f"✅ Attempting to connect to {port} @ {DEFAULT_BAUD}...")
        
        try:
            with serial.Serial(port, DEFAULT_BAUD, timeout=2) as ser:
                print(f"🚀 Connected to {port}!")
                time.sleep(0.5)  # Give Arduino time to initialize
                
                # Clear buffer
                ser.reset_input_buffer()
                
                while True:
                    try:
                        line = ser.readline().decode(errors="ignore").strip()
                        if not line:
                            # No data yet, just loop
                            continue

                        # Expect JSON object per line from Arduino
                        if not (line.startswith("{") and line.endswith("}")):
                            # some boards might send extra text; try to find JSON substring
                            try:
                                start = line.index("{")
                                end = line.rindex("}") + 1
                                line = line[start:end]
                            except Exception:
                                continue

                        try:
                            data = json.loads(line)
                        except Exception:
                            # malformed json - skip
                            continue

                        # Firmware version if provided by the device (optional)
                        firmware = data.get("firmware", None)

                        # Robust conversions
                        temp = safe_float(data.get("temperature"))
                        humidity = safe_float(data.get("humidity"))
                        pressure = safe_float(data.get("pressure"))
                        rain_raw = data.get("rain_value", 0)
                        rain_digital = int(data.get("rain_digital", 1))

                        # Convert raw rain analog to mm using a simple calibration
                        # 0-1023 -> 0-10mm (example)
                        try:
                            rain_raw_f = float(rain_raw)
                        except:
                            rain_raw_f = 0.0

                        # If digital sensor says DRY (1), force 0mm
                        if rain_digital == 1:
                            rainfall_mm = 0.0
                        else:
                            # It is WET (0). Map analog value.
                            # Usually lower analog value = wetter? Or higher? 
                            # Assuming higher = wetter based on previous logic (rain_raw_f / 1023)
                            # Previous logic: if > 50: (rain_raw_f / 1023.0) * 10.0
                            # We will apply this scaling consistently.
                            rainfall_mm = round((rain_raw_f / 1023.0) * 10.0, 2)

                        status = "Dry" if rain_digital == 1 else "Wet"

                        row = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "temperature_c": temp,
                            "humidity_perc": humidity,
                            "pressure_hpa": pressure,
                            "rainfall_mm": rainfall_mm,
                            "status": status
                        }

                        insert_reading(row)
                        # Minimal console log
                        print(f"[{row['timestamp']}] Inserted: T={temp}C H={humidity}% P={pressure}hPa Rain={rainfall_mm}mm")
                        
                        # Push to remote (Bridge Mode)
                        push_to_remote(row)
                        
                    except serial.SerialException as e:
                        print(f"❌ Serial connection lost: {e}")
                        break # Break inner loop to reconnect
                    except Exception as e:
                        print(f"⚠️ Error processing line: {e}")
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"❌ Failed to connect to {port}: {e}")
            time.sleep(2)

def push_to_remote(row):
    """
    Push reading to remote API if configured.
    """
    remote_url = os.getenv("REMOTE_API_URL")
    secret = os.getenv("BRIDGE_SECRET")
    
    if not remote_url:
        return

    try:
        # Ensure URL ends with /api/sensor-data if not fully specified
        # But user might put full URL. Let's assume full URL or append if needed.
        # Ideally user sets REMOTE_API_URL="https://app.onrender.com/api/sensor-data"
        
        headers = {
            "Content-Type": "application/json",
            "X-Bridge-Secret": secret or ""
        }
        
        # We need to import requests. It is in requirements.txt
        import requests
        
        resp = requests.post(remote_url, json=row, headers=headers, timeout=3)
        if resp.status_code == 200:
            print(f"☁️  Pushed to cloud: {resp.status_code}")
        else:
            print(f"⚠️  Cloud push failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"⚠️  Cloud push error: {e}")


if __name__ == "__main__":
    try:
        run_serial_loop()
    except KeyboardInterrupt:
        print("Shutting down serial reader.")
