"""
Training script for ML temperature prediction.
This file should NOT run during FastAPI import.
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

DATA_FILE = "raw_data.csv"
MODEL_FILE = "trained_weather_model.pkl"

FEATURES = [
    "temperature_c",
    "humidity_perc",
    "pressure_hpa",
    "rainfall_mm",
    "hour_of_day",
    "dayofyear",
    "temp_roll_3",
    "temp_roll_6",
    "pressure_roll_3",
    "rain_roll_3",
    "pressure_diff_1"
]

def train_model():
    print("Loading dataset:", DATA_FILE)

    if not os.path.exists(DATA_FILE):
        print("❌ ERROR: CSV file not found!")
        return

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        print("❌ ERROR: CSV file is EMPTY!")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # numeric conversions
    for c in ["temperature_c", "humidity_perc", "pressure_hpa", "rainfall_mm"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["temperature_c", "humidity_perc", "pressure_hpa"])

    # Features
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["dayofyear"] = df["timestamp"].dt.dayofyear

    df["temp_roll_3"] = df["temperature_c"].rolling(window=3, min_periods=1).mean()
    df["temp_roll_6"] = df["temperature_c"].rolling(window=6, min_periods=1).mean()
    df["pressure_roll_3"] = df["pressure_hpa"].rolling(window=3, min_periods=1).mean()
    df["rain_roll_3"] = df["rainfall_mm"].rolling(window=3, min_periods=1).mean()
    df["pressure_diff_1"] = df["pressure_hpa"].diff().fillna(0)

    df["target_next_temp"] = df["temperature_c"].shift(-1)
    df = df.dropna(subset=["target_next_temp"])
    df = df.dropna(subset=FEATURES)

    X = df[FEATURES]
    y = df["target_next_temp"]

    print("Training with features:", FEATURES)
    print("Dataset size:", len(X))

    split_idx = int(len(X) * 0.9)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=3,
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    print(f"Model MAE: {mae:.3f}°C")

    payload = {
        "model": model,
        "features": FEATURES,
        "mae": float(mae),
        "trained_on_rows": int(len(X_train)),
    }

    joblib.dump(payload, MODEL_FILE)
    print("🎉 Training complete. Saved:", MODEL_FILE)


# ----------------------------------------
# ❗ IMPORTANT: ONLY RUN IF EXECUTED DIRECTLY
# ----------------------------------------
if __name__ == "__main__":
    train_model()
