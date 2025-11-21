# api/combined.py
from fastapi import APIRouter
from .latest_sensor import get_latest_sensor
from .weather_api import get_weatherapi_now, get_weatherapi_7day
from .ml_forecast import get_ml_forecast

router = APIRouter()

@router.get("/combined")
def combined_weather():
    # ============================================================
    # 1. 7-DAY FORECAST (WeatherAPI) - Fetch first for sunrise/sunset
    # ============================================================
    daily = get_weatherapi_7day() or []
    if not isinstance(daily, list):
        daily = []

    # Get today's astro data if available
    today_astro = {}
    if daily:
        today_astro = {
            "sunrise": daily[0].get("sunrise"),
            "sunset": daily[0].get("sunset")
        }

    latest = get_latest_sensor()
    
    # Always fetch current API weather if we might need it for fallbacks (wind)
    # or if sensor is missing.
    w_now = get_weatherapi_now() or {}
    w_current_api = w_now.get("current", {})

    if latest:
        # From ESP32 sensor
        # Fallback to API for wind if sensor doesn't have it
        wind_val = latest.get("wind_speed_kph") or latest.get("wind_kph")
        if wind_val is None:
            wind_val = w_current_api.get("wind_kph")

        current = {
            "temp": latest.get("temperature_c"),
            "feels_like": latest.get("temperature_c"), # Sensor doesn't calculate feels_like, use temp
            "humidity": latest.get("humidity_perc"),
            "pressure": latest.get("pressure_hpa"),
            "wind": wind_val,
            "rainfall": latest.get("rainfall_mm") or 0,
            "condition": latest.get("status") or "Unknown", # Fix: status -> condition
            "sunrise": today_astro.get("sunrise"),
            "sunset": today_astro.get("sunset"),
        }
    else:
        # Fallback to WeatherAPI
        cond = w_current_api.get("condition")
        if isinstance(cond, dict):
            cond = cond.get("text")
        if cond is None:
            cond = "Unknown"

        current = {
            "temp": w_current_api.get("temperature_c") or w_current_api.get("temp_c"),
            "feels_like": w_current_api.get("feelslike_c"),
            "humidity": w_current_api.get("humidity"),
            "pressure": w_current_api.get("pressure_hpa") or w_current_api.get("pressure_mb"),
            "wind": w_current_api.get("wind_kph"),
            "rainfall": w_current_api.get("precip_mm") or 0,
            "condition": cond,
            "sunrise": today_astro.get("sunrise"),
            "sunset": today_astro.get("sunset"),
        }

    # ============================================================
    # 3. ML FORECAST (7-day prediction)
    # ============================================================
    ml = get_ml_forecast() or {}
    ml_list = ml.get("forecast", [])

    if not isinstance(ml_list, list):
        ml_list = []

    # Normalize ML items
    normalized_ml = []
    for d in ml_list:
        normalized_ml.append({
            "day": d.get("day"),
            "temp_high_c": d.get("temp_high_c"),
            "temp_low_c": d.get("temp_low_c"),
            "rain_prob_perc": d.get("rain_prob_perc"),
            "condition": d.get("condition", "ML Prediction"),
        })
    ml_list = normalized_ml
    
    # MERGE: Fill missing days in 'daily' with ML data
    existing_dates = set(d.get("day") for d in daily)
    for ml_item in ml_list:
        if ml_item.get("day") not in existing_dates:
            # Add ML prediction as a fallback for missing API days
            daily.append(ml_item)
            existing_dates.add(ml_item.get("day"))
            
    # Sort by date to ensure order
    try:
        daily.sort(key=lambda x: x.get("day", ""))
    except:
        pass
        
    # Limit to 7 days
    daily = daily[:7]

    # ============================================================
    # 4. CHART DATA (always 7 days)
    # ============================================================
    # Labels always use ML first, then fallback to WeatherAPI
    if ml_list:
        labels = [d["day"] for d in ml_list]
        ai_vals = [d["temp_high_c"] for d in ml_list]
    else:
        labels = [d["day"] for d in daily]
        ai_vals = []

    # Pad API highs/lows to 7 if shorter
    api_high = [d.get("temp_high_c") for d in daily]
    api_low = [d.get("temp_low_c") for d in daily]
    
    # Get real historical trend data from database
    from db.db import get_daily_trends
    trends_df = get_daily_trends(days=7)
    
    # Extract humidity, pressure, and rainfall trends from historical data
    humidity_trend = []
    pressure_trend = []
    rainfall_trend = []
    
    if not trends_df.empty:
        # Use historical data
        humidity_trend = trends_df['avg_humidity'].fillna(0).tolist()
        pressure_trend = trends_df['avg_pressure'].fillna(0).tolist()
        rainfall_trend = trends_df['total_rainfall'].fillna(0).tolist()
    
    # Pad to 7 days if needed
    while len(humidity_trend) < 7:
        humidity_trend.append(None)
    while len(pressure_trend) < 7:
        pressure_trend.append(None)
    while len(rainfall_trend) < 7:
        rainfall_trend.append(0)

    # ensure length 7 (UI expects equal chart lengths)
    while len(api_high) < 7:
        api_high.append(None)
    while len(api_low) < 7:
        api_low.append(None)
    while len(labels) < 7:
        labels.append("")

    # ============================================================
    # 5. FINAL RESPONSE (UI expects these keys!)
    # ============================================================
    return {
        "current": current,
        "daily": daily,
        "sensor_status": "Connected" if latest else "Disconnected",
        "chart": {
            "labels": labels,
            "AI": ai_vals,
            "API_high": api_high,
            "API_low": api_low,
            "humidity": humidity_trend[:7],  # Limit to 7
            "pressure": pressure_trend[:7],
            "rainfall": rainfall_trend[:7]
        }
    }
