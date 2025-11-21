# api/gemini_forecast.py
from fastapi import APIRouter
from google import genai
from dotenv import load_dotenv
import os, json

load_dotenv()
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY missing in .env")

# Initialize new Gemini Client (2025 version)
client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_forecast(city="Kolkata"):
    """Generate a 7-day weather forecast using the new Gemini 2.x API."""
    if not GEMINI_API_KEY:
        return None

    prompt = f"""
    Generate a strict JSON array of 7 weather forecast objects for {city}.
    Format:
    [
      {{
        "day": "YYYY-MM-DD",
        "temp_high_c": 0,
        "temp_low_c": 0,
        "rain_prob_perc": 0,
        "condition": "Sunny"
      }}
    ]
    Only output JSON. No explanation. No markdown.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",   # FAST + FREE model
            contents=prompt
        )

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "")

        data = json.loads(raw)

        return {"forecast": data}

    except Exception as e:
        print("Gemini Forecast Error:", e)
        return None


@router.get("/gemini")
def api_gemini():
    return get_gemini_forecast() or {"error": "Gemini unavailable"}
