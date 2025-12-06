from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.combined import router as combined_router
from api.weather_api import router as weather_router
from api.latest_sensor import router as sensor_router
from api.ml_forecast import router as ml_router
from api.populate_data import router as populate_router
from api.ingest import router as ingest_router

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
app.include_router(populate_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")

from nicegui import ui
# Import the UI module to register pages
import ui.ui

# Mount NiceGUI to FastAPI
# NOTE: We remove the root route so NiceGUI can take over '/'
ui.run_with(
    app,
    title="WeatherAI Dashboard",
    storage_secret="weather-secret-key",
)
