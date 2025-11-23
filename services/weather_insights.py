"""
Weather Insights Generator
Generates natural language weather summaries and recommendations
"""

def generate_summary(current, forecast, sensor_status="Unknown"):
    """Generate a natural language weather summary with recommendations."""
    
    # Extract current conditions
    temp = current.get("temp")
    humidity = current.get("humidity")
    pressure = current.get("pressure")
    rainfall = current.get("rainfall", 0)
    condition = current.get("condition", "").lower()
    
    # Build summary parts
    summary_parts = []
    recommendations = []
    
    # Temperature insight
    temp_insight = get_temperature_insight(temp)
    if temp_insight:
        summary_parts.append(temp_insight)
    
    # Humidity insight
    if humidity:
        if humidity > 80:
            summary_parts.append(f"Very humid at {humidity}%")
            recommendations.append("💧 Stay hydrated")
        elif humidity > 60:
            summary_parts.append(f"Moderately humid at {humidity}%")
        elif humidity < 30:
            summary_parts.append(f"Dry air at {humidity}%")
            recommendations.append("🧴 Use moisturizer")
    
    # Rain insight
    rain_insight, rain_rec = get_rain_insight(rainfall, condition, forecast)
    if rain_insight:
        summary_parts.append(rain_insight)
    if rain_rec:
        recommendations.append(rain_rec)
    
    # Pressure insight
    if pressure:
        if pressure < 1000:
            summary_parts.append("Low pressure system")
            recommendations.append("⛈️ Storms possible")
        elif pressure > 1020:
            summary_parts.append("High pressure")
    
    # Forecast trend
    if forecast and len(forecast) > 0:
        today_temp = temp or 0
        tomorrow = forecast[0] if len(forecast) > 0 else {}
        tomorrow_high = tomorrow.get("temp_high_c") or tomorrow.get("high")
        
        if tomorrow_high and today_temp:
            diff = tomorrow_high - today_temp
            if diff > 3:
                summary_parts.append("Warming trend ahead")
            elif diff < -3:
                summary_parts.append("Cooling trend expected")
    
    # Sensor status
    status_emoji = "🟢" if sensor_status == "Connected" else "🔴"
    
    # Combine into summary
    if summary_parts:
        summary = ". ".join(summary_parts[:3]) + "."
    else:
        summary = "Weather data is being collected."
    
    return {
        "summary": summary,
        "recommendations": recommendations[:3],  # Max 3 recommendations
        "status_emoji": status_emoji,
        "status_text": sensor_status
    }


def get_temperature_insight(temp):
    """Get temperature-based insight."""
    if not temp:
        return None
    
    if temp >= 35:
        return f"Very hot at {temp:.0f}°C"
    elif temp >= 30:
        return f"Hot weather at {temp:.0f}°C"
    elif temp >= 25:
        return f"Warm at {temp:.0f}°C"
    elif temp >= 20:
        return f"Pleasant {temp:.0f}°C"
    elif temp >= 15:
        return f"Mild at {temp:.0f}°C"
    elif temp >= 10:
        return f"Cool at {temp:.0f}°C"
    elif temp >= 5:
        return f"Cold at {temp:.0f}°C"
    else:
        return f"Very cold at {temp:.0f}°C"


def get_rain_insight(rainfall, condition, forecast):
    """Get rain-related insights and recommendations."""
    insight = None
    recommendation = None
    
    # Current rain
    if rainfall and rainfall > 0:
        if rainfall > 10:
            insight = f"Heavy rain ({rainfall:.1f}mm)"
            recommendation = "🌂 Umbrella essential"
        elif rainfall > 2:
            insight = f"Moderate rain ({rainfall:.1f}mm)"
            recommendation = "🌂 Bring umbrella"
        else:
            insight = f"Light rain ({rainfall:.1f}mm)"
    
    # Check condition
    if "rain" in condition or "drizzle" in condition:
        if not insight:
            insight = "Rainy conditions"
        if not recommendation:
            recommendation = "🌂 Bring umbrella"
    
    # Check forecast for rain
    if forecast and not recommendation:
        for day in forecast[:2]:  # Check next 2 days
            rain_prob = day.get("rain_prob_perc", 0)
            if rain_prob and rain_prob > 60:
                recommendation = "🌂 Rain likely soon"
                break
    
    return insight, recommendation


def get_recommendations(temp, humidity, condition):
    """Get actionable recommendations based on conditions."""
    recs = []
    
    # Temperature-based
    if temp:
        if temp > 30:
            recs.append("☀️ Wear sunscreen")
            recs.append("💧 Stay hydrated")
        elif temp < 10:
            recs.append("🧥 Wear warm clothes")
    
    # Humidity-based
    if humidity:
        if humidity > 80:
            recs.append("💨 Expect muggy conditions")
        elif humidity < 30:
            recs.append("🧴 Moisturize skin")
    
    # Condition-based
    if condition:
        if "sun" in condition or "clear" in condition:
            recs.append("😎 Sunglasses recommended")
        elif "storm" in condition:
            recs.append("⚠️ Stay indoors if possible")
    
    return recs[:3]  # Return max 3
