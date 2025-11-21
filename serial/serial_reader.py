import serial
import serial.tools.list_ports
import json
from datetime import datetime
import time
import os
from db import init_db, insert_reading

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

PORT = find_port()
if PORT is None:
    print("No Arduino found. Set SERIAL_PORT env var or plug in device.")
    exit(1)

try:
    ser = serial.Serial(PORT, DEFAULT_BAUD, timeout=1)
except Exception as e:
    print("Failed to open serial port:", e)
    exit(1)

print(f"Listening on {PORT} @ {DEFAULT_BAUD} baud")

def safe_float(v, default=0.0):
    try:
        return float(v)
    except:
        return default

while True:
    try:
        line = ser.readline().decode(errors="ignore").strip()
        if not line:
            time.sleep(0.05)
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
        temp = safe_float(data.get("temperature", 0.0))
        humidity = safe_float(data.get("humidity", 0.0))
        pressure = safe_float(data.get("pressure", 0.0))
        rain_raw = data.get("rain_value", 0)
        rain_digital = int(data.get("rain_digital", 1))

        # Convert raw rain analog to mm using a simple calibration (adjust if you have real calibration)
        # If raw is already small (0/1) treat as mm directly
        try:
            rain_raw_f = float(rain_raw)
        except:
            rain_raw_f = 0.0

        if rain_raw_f > 50:
            # map 0-1023 -> 0-10mm (example). Adjust to your sensor calibration.
            rainfall_mm = round((rain_raw_f / 1023.0) * 10.0, 2)
        else:
            rainfall_mm = round(rain_raw_f, 2)

        status = "Dry" if rain_digital == 1 else "Wet"

        row = {
            "timestamp": datetime.now().isoformat(),
            "temperature_c": temp,
            "humidity_perc": humidity,
            "pressure_hpa": pressure,
            "rainfall_mm": rainfall_mm,
            "status": status
        }

        insert_reading(row)
        # Minimal console log (can be noisy if sampling fast)
        print(f"[{row['timestamp']}] Inserted: T={temp}C H={humidity}% P={pressure}hPa Rain={rainfall_mm}mm Firmware={firmware or 'unknown'}")
        time.sleep(0.15)

    except KeyboardInterrupt:
        print("Shutting down serial reader.")
        break
    except Exception as e:
        print("Serial read error:", str(e))
        time.sleep(1)
