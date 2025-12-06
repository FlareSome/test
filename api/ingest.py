from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
from db.db import insert_reading

router = APIRouter()

# Simple security: Require a secret key in headers
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "my-secret-bridge-key")

class SensorData(BaseModel):
    timestamp: Optional[str] = None
    temperature_c: Optional[float] = None
    humidity_perc: Optional[float] = None
    pressure_hpa: Optional[float] = None
    rainfall_mm: Optional[float] = None
    status: Optional[str] = "Unknown"

@router.post("/sensor-data")
async def ingest_sensor_data(
    data: SensorData, 
    x_bridge_secret: str = Header(None, alias="X-Bridge-Secret")
):
    """
    Endpoint to receive sensor data from the local bridge.
    """
    # 1. Verify Secret
    if x_bridge_secret != BRIDGE_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Bridge Secret")

    # 2. Prepare row
    row = {
        "timestamp": data.timestamp or datetime.now().isoformat(),
        "temperature_c": data.temperature_c,
        "humidity_perc": data.humidity_perc,
        "pressure_hpa": data.pressure_hpa,
        "rainfall_mm": data.rainfall_mm,
        "status": data.status
    }

    # 3. Insert into DB
    try:
        insert_reading(row)
        return {"status": "success", "message": "Data ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
