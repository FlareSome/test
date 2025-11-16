import serial
import json
import pandas as pd
from datetime import datetime
import time

CSV_FILE = "raw_data.csv"

# CSV columns
columns = [
    "timestamp",
    "temperature_c",
    "humidity_perc",
    "pressure_hpa",
    "rainfall_mm",
    "status"
]

# Load or create CSV
try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame(columns=columns)
    df.to_csv(CSV_FILE, index=False)

print("Listening on /dev/ttyACM0 ...")
ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

last_entry = None

while True:
    try:
        line = ser.readline().decode("utf-8").strip()

        # ignore empty lines
        if not line:
            continue

        # ignore garbage
        if not (line.startswith("{") and line.endswith("}")):
            continue

        # Try decode JSON
        try:
            data = json.loads(line)
        except:
            print("Skipped invalid JSON:", line)
            continue

        # Build a clean entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "temperature_c": float(data.get("temperature", 0) or 0),
            "humidity_perc": float(data.get("humidity", 0) or 0),
            "pressure_hpa": float(data.get("pressure", 0) or 0),
            "rainfall_mm": float((data.get("rain_value", 0) or 0) / 10.0),
            "status": "Dry" if data.get("rain_digital", 1) == 1 else "Wet"
        }

        # Ignore duplicates
        if entry == last_entry:
            time.sleep(0.3)
            continue

        last_entry = entry

        # Append to existing dataframe (no reload)
        df.loc[len(df)] = entry
        df.to_csv(CSV_FILE, index=False)

        print("Saved:", entry)
        time.sleep(0.3)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
