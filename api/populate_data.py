# api/populate_data.py
from fastapi import APIRouter
from datetime import datetime, timedelta
import random
from db.db import init_db, insert_reading

router = APIRouter()

@router.get("/populate_sample_data")
def populate_sample_data(days: int = 7):
    """Generate sample historical data for charts"""
    try:
        init_db()
        
        # Baseline values
        baseline = {"temp": 25, "humidity": 50, "pressure": 1013}
        now = datetime.now()
        total = 0
        
        for day in range(days, 0, -1):
            for hour in range(24):
                timestamp = now - timedelta(days=day, hours=(24-hour))
                hour_factor = abs(12 - hour) / 12
                temp_cycle = -4 * hour_factor
                
                reading = {
                    "timestamp": timestamp.isoformat(),
                    "temperature_c": baseline["temp"] + random.uniform(-3, 3) + temp_cycle,
                    "humidity_perc": max(20, min(100, baseline["humidity"] + random.uniform(-10, 10))),
                    "pressure_hpa": baseline["pressure"] + random.uniform(-5, 5),
                    "rainfall_mm": random.choice([0, 0, 0, 0, random.uniform(0, 2)]),
                    "status": random.choice(["Clear", "Clear", "Partly Cloudy", "Cloudy", "Mist"])
                }
                insert_reading(reading)
                total += 1
        
        return {
            "status": "success",
            "message": f"Generated {total} sample readings for {days} days",
            "readings_count": total
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
