#!/usr/bin/env python3
"""
Populate database with sample historical weather data for chart display.
This creates 7 days of simulated sensor readings based on current weather.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import init_db, insert_reading
import requests

def get_current_weather():
    """Get current weather from API"""
    try:
        response = requests.get("http://localhost:8000/api/combined", timeout=5)
        data = response.json()
        current = data.get("api_data", {})
        return {
            "temp": current.get("temp", 25),
            "humidity": current.get("humidity", 50),
            "pressure": current.get("pressure", 1013),
            "rainfall": current.get("rainfall", 0)
        }
    except:
        # Fallback defaults
        return {
            "temp": 25,
            "humidity": 50,
            "pressure": 1013,
            "rainfall": 0
        }

def generate_sample_data(days=7, readings_per_day=24):
    """Generate sample historical data"""
    print(f"🔧 Generating {days} days of sample data...")
    
    # Get current weather as baseline
    baseline = get_current_weather()
    print(f"📊 Baseline: {baseline['temp']}°C, {baseline['humidity']}%, {baseline['pressure']} hPa")
    
    # Initialize database
    init_db()
    
    # Generate readings
    now = datetime.now()
    total_readings = 0
    
    for day in range(days, 0, -1):  # Go backwards from 7 days ago to now
        for hour in range(readings_per_day):
            # Calculate timestamp
            timestamp = now - timedelta(days=day, hours=(24-hour))
            
            # Add some realistic variation
            temp_variation = random.uniform(-3, 3)
            humidity_variation = random.uniform(-10, 10)
            pressure_variation = random.uniform(-5, 5)
            
            # Simulate daily temperature cycle (cooler at night)
            hour_factor = abs(12 - hour) / 12  # 0 at noon, 1 at midnight
            temp_cycle = -4 * hour_factor  # Up to -4°C at night
            
            reading = {
                "timestamp": timestamp.isoformat(),
                "temperature_c": baseline["temp"] + temp_variation + temp_cycle,
                "humidity_perc": max(20, min(100, baseline["humidity"] + humidity_variation)),
                "pressure_hpa": baseline["pressure"] + pressure_variation,
                "rainfall_mm": random.choice([0, 0, 0, 0, random.uniform(0, 2)]),  # Occasional rain
                "status": random.choice(["Clear", "Clear", "Partly Cloudy", "Cloudy", "Mist"])
            }
            
            insert_reading(reading)
            total_readings += 1
    
    print(f"✅ Inserted {total_readings} sample readings")
    print(f"📅 Date range: {(now - timedelta(days=days)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
    print(f"🎯 Charts should now display data!")

if __name__ == "__main__":
    print("=" * 60)
    print("Weather Data Generator")
    print("=" * 60)
    generate_sample_data(days=7, readings_per_day=24)
    print("=" * 60)
    print("✨ Done! Refresh your dashboard to see the charts.")
