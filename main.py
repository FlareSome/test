from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import os
from datetime import datetime
from nicegui import ui
import ui.ui as ui_module # Register pages
from db.db import insert_reading, init_db

from api.combined import router as combined_router
from api.weather_api import router as weather_router
from api.latest_sensor import router as sensor_router
from api.ml_forecast import router as ml_router

# Ensure DB exists
init_db()

app = FastAPI(title="WeatherStack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only these — Gemini removed
app.include_router(sensor_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(ml_router, prefix="/api")
app.include_router(combined_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "running"}

# --- Mock Sensor Service ---
class MockSensorService:
    def __init__(self):
        self.running = False
        self.task = None
        # Initial realistic values
        self.temp = 25.0
        self.humidity = 60.0
        self.pressure = 1013.0
        self.rain_accum = 0.0

    async def start(self):
        if self.running: return
        self.running = True
        self.task = asyncio.create_task(self._loop())
        print("🤖 Mock Sensor Service Started")

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("🤖 Mock Sensor Service Stopped")

    async def _loop(self):
        while self.running:
            try:
                # Random Walk Logic
                # Temp: drift between 20-35
                delta_t = random.uniform(-0.5, 0.5)
                self.temp += delta_t
                self.temp = max(20.0, min(35.0, self.temp))

                # Humidity: drift between 40-90
                delta_h = random.uniform(-2.0, 2.0)
                self.humidity += delta_h
                self.humidity = max(40.0, min(90.0, self.humidity))

                # Pressure: drift between 1000-1020
                delta_p = random.uniform(-0.5, 0.5)
                self.pressure += delta_p
                self.pressure = max(1000.0, min(1020.0, self.pressure))

                # Rain: mostly 0, occasional showers
                # 5% chance of rain if humidity > 70
                rain_mm = 0.0
                if self.humidity > 70 and random.random() < 0.05:
                    rain_mm = random.uniform(0.1, 2.0)
                
                status = "Wet" if rain_mm > 0 else "Dry"

                row = {
                    "timestamp": datetime.now().isoformat(),
                    "temperature_c": round(self.temp, 1),
                    "humidity_perc": round(self.humidity, 1),
                    "pressure_hpa": round(self.pressure, 1),
                    "rainfall_mm": round(rain_mm, 2),
                    "status": status
                }
                
                # Insert into DB
                # Run in executor to avoid blocking event loop with sqlite
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, lambda: insert_reading(row))
                
                # print(f"🤖 Mock Data: {row}") # Debug
                
                await asyncio.sleep(5) # Update every 5 seconds

            except Exception as e:
                print(f"🤖 Mock Service Error: {e}")
                await asyncio.sleep(5)

mock_service = MockSensorService()

@app.on_event("startup")
async def startup_event():
    # Check if we should enable mock sensor
    # Default to True if MOCK_SENSOR is set, or if SERIAL_PORT is not set (implying cloud)
    should_mock = os.getenv("MOCK_SENSOR", "false").lower() == "true"
    
    if should_mock:
        await mock_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    await mock_service.stop()

# Mount NiceGUI
ui.run_with(app, title="WeatherAI Dashboard", storage_secret="weather_secret")
