# api/ml_forecast.py
import os
import joblib
import pandas as pd
from fastapi import APIRouter
from db.db import get_latest_reading

router = APIRouter()

# Correct model path under /db/
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "db",
    "trained_weather_model.pkl"
)

def load_model():
    """Load RandomForest payload safely."""
    try:
        if not os.path.exists(MODEL_PATH):
            print("ML model missing at:", MODEL_PATH)
            return None, None

        payload = joblib.load(MODEL_PATH)
        model = payload.get("model")
        features = payload.get("features")
        return model, features

    except Exception as e:
        print("Model load error:", e)
        return None, None


def build_feature_rows(latest, features):
    """Builds 7 feature rows for prediction."""
    rows = []
    base_day = pd.to_datetime(latest["timestamp"]).dayofyear

    for i in range(1, 8):
        row = {}
        for f in features:
            if f == "dayofyear":
                row[f] = base_day + i
            else:
                row[f] = latest.get(f, latest.get(f.replace("_c", ""), 0))
        rows.append(row)

    return pd.DataFrame(rows)[features]


def get_ml_forecast():
    """Generates a 7-day ML forecast."""
    model, features = load_model()
    if model is None or not features:
        return {"forecast": []}

    df = get_latest_reading(1)
    if df.empty:
        return {"forecast": []}

    latest = df.iloc[0].to_dict()

    X = build_feature_rows(latest, features)
    preds = model.predict(X)

    out = []
    for i, p in enumerate(preds, start=1):
        day_date = (pd.Timestamp(latest["timestamp"]) + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        out.append({
            "day": day_date,
            "temp_high_c": float(p),
            "temp_low_c": float(p) - 3,
            "rain_prob_perc": None,
            "condition": "ML Prediction"
        })

    return {"forecast": out}


@router.get("/ml_forecast")
def ml_forecast_endpoint():
    """API endpoint used by UI."""
    return get_ml_forecast()
