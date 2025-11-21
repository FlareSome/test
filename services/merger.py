from datetime import datetime, timedelta

def normalize_condition(cond: str) -> str:
    if not cond: return "Unknown"
    cond = cond.lower()
    if "rain" in cond: return "Rain"
    if "storm" in cond: return "Storm"
    if "snow" in cond: return "Snow"
    if "cloud" in cond: return "Cloudy"
    if "clear" in cond or "sun" in cond: return "Sunny"
    return cond.title()

def unify_sources(latest, wapi_now, wapi_7day, gem, ml):
    # ---- CURRENT SECTION ----
    current = {
        "temp": latest.get("temperature_c") if latest else None,
        "humidity": latest.get("humidity_perc") if latest else None,
        "pressure": latest.get("pressure_hpa") if latest else None,
        "wind": latest.get("wind_speed_kph") if latest else None,
        "feels_like": None,
        "condition": "Unknown",
        "sunrise": None,
        "sunset": None
    }

    # Overwrite/complete with WeatherAPI
    if wapi_now and "current" in wapi_now:
        cur = wapi_now["current"]
        current["temp"] = current["temp"] or cur.get("temperature_c")
        current["humidity"] = current["humidity"] or cur.get("humidity")
        current["pressure"] = current["pressure"] or cur.get("pressure_hpa")
        current["wind"] = current["wind"] or cur.get("wind_kph")
        current["feels_like"] = cur.get("feelslike_c")
        cond = cur.get("condition", "")
        if isinstance(cond, dict): cond = cond.get("text")
        current["condition"] = normalize_condition(cond)

    # Sunrise/sunset
    if wapi_7day:
        d0 = wapi_7day[0]
        current["sunrise"] = d0.get("sunrise")
        current["sunset"] = d0.get("sunset")

    # ---- HOURLY SECTION ----
    hourly = []
    # If WeatherAPI hourly exists, use it
    if wapi_now and wapi_now.get("forecast") and "forecastday" in wapi_now["forecast"]:
        try:
            hours = wapi_now["forecast"]["forecastday"][0]["hour"]
            for h in hours[:12]:
                t = h.get("time")
                hour = datetime.fromisoformat(t).strftime("%I %p")
                cond = h.get("condition", {})
                if isinstance(cond, dict): cond = cond.get("text")
                hourly.append({
                    "hour": hour,
                    "temp": h.get("temp_c"),
                    "cond": normalize_condition(cond)
                })
        except:
            pass

    # ---- DAILY SECTION ----
    daily = []
    if wapi_7day:
        for d in wapi_7day:
            dayname = datetime.strptime(d["day"], "%Y-%m-%d").strftime("%a")
            daily.append({
                "day": dayname,
                "high": d.get("temp_high_c"),
                "low": d.get("temp_low_c"),
                "cond": normalize_condition(d.get("condition"))
            })

    # ---- CHART SECTION ----
    chart = {"labels": [], "AI": [], "API_high": [], "API_low": []}

    if ml and "forecast" in ml:
        chart["labels"] = [f["day"] for f in ml["forecast"]]
        chart["AI"] = [f["temp_high_c"] for f in ml["forecast"]]

    if wapi_7day:
        api_labels = [d["day"] for d in wapi_7day]
        chart["API_high"] = [d["temp_high_c"] for d in wapi_7day]
        chart["API_low"] = [d["temp_low_c"] for d in wapi_7day]

        if not chart["labels"]:
            chart["labels"] = api_labels

    return {
        "current": current,
        "hourly": hourly,
        "daily": daily,
        "chart": chart
    }
