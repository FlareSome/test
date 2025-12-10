# ui/ui.py
# Modern Glassmorphism Weather Dashboard
from nicegui import ui
import requests
import os
import sys
from datetime import datetime
import plotly.graph_objects as go
import asyncio
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.theme_manager import ThemeManager

# --- Configuration ---
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
CITY = os.getenv("CITY_NAME", "New Town, West Bengal")
REFRESH_SECONDS = 2  # Fast refresh for sensor data (API is cached)

# --- Styling Constants ---
# Using Tailwind arbitrary values in code, but defining common colors here
THEME_COLOR = "#60A5FA"  # Blue-400
TEXT_COLOR = "#F1F5F9"   # Slate-100
MUTED_COLOR = "#94A3B8"  # Slate-400

# --- Helper Functions ---
def safe_get(path, fallback=None):
    try:
        r = requests.get(API_BASE + path, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ui] fetch error {path}: {e}")
        return fallback

def _format_temp(v):
    try:
        return f"{float(v):.0f}°"
    except:
        return "—"

def _format_time(t):
    try:
        if not t: return "—"
        # Check if already formatted
        if "AM" in t or "PM" in t: return t
        # Handle ISO or simple HH:MM
        if "T" in t:
            dt = datetime.fromisoformat(t)
            return dt.strftime("%I:%M %p").lstrip("0")
        if len(t.split(":")) >= 2:
            dt = datetime.strptime(t[:5], "%H:%M")
            return dt.strftime("%I:%M %p").lstrip("0")
        return t
    except:
        return "—"

def _get_weather_icon(cond):
    """Returns a tuple (Emoji, CSS Class for color, Animation Class)"""
    cond = (cond or "").lower()
    if "storm" in cond or "thunder" in cond: 
        return "⛈️", "text-yellow-300", "weather-icon-storm"
    if "rain" in cond or "drizzle" in cond: 
        return "🌧️", "text-blue-300", "weather-icon-rain"
    if "snow" in cond or "sleet" in cond: 
        return "❄️", "text-white", "weather-icon-snow"
    if "clear" in cond or "sun" in cond: 
        return "☀️", "text-orange-300", "weather-icon-sunny"
    if "partly" in cond: 
        return "🌤️", "text-yellow-100", "weather-icon-sunny"
    if "cloud" in cond or "overcast" in cond: 
        return "☁️", "text-gray-300", "weather-icon-cloud"
    if "fog" in cond or "mist" in cond: 
        return "🌫️", "text-gray-400", "weather-icon-cloud"
    if "wet" in cond: 
        return "🌧️", "text-blue-400", "weather-icon-rain"
    if "dry" in cond: 
        return "☁️", "text-gray-200", "weather-icon-cloud"
    return "🌡️", "text-blue-200", ""

def create_sparkline(data, color='#3B82F6'):
    """Create a mini sparkline chart for detail cards."""
    if not data or len(data) == 0:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=40
    )
    
    return fig

# --- CSS ---
APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

body {
    font-family: 'Inter', sans-serif;
    margin: 0;
}

/* The Glass Card Effect */
.glass-panel {
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 1.5rem;
}

.glass-header {
    backdrop-filter: blur(10px);
    margin: 1rem;
    border-radius: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Custom Scrollbar for horizontal lists */
.hide-scroll::-webkit-scrollbar {
    height: 6px;
}
.hide-scroll::-webkit-scrollbar {
    border-radius: 10px;
}

/* Loading Screen Animations */
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #000000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    transition: opacity 0.8s ease-out, visibility 0.8s ease-out;
}

.loading-screen.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}

/* Custom Loader Animation */
.loader {
    width: 96px;
    aspect-ratio: 1;
    position: relative;
    animation: l13-0 2s linear infinite;
}

.loader::before,
.loader::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: radial-gradient(at 30% 30%, #0000, #000a) rgba(255, 255, 255, 0.3);
    animation: l13-1 0.5s cubic-bezier(.5, -500, .5, 500) infinite;
}

.loader::after {
    animation-delay: -0.15s;
}

@keyframes l13-0 { 
    100% { transform: rotate(360deg); } 
}

@keyframes l13-1 { 
    100% { transform: translate(0.5px); } 
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main-content {
    opacity: 0;
    animation: fadeInUp 1s ease-out 0.4s forwards;
}

/* ========================================
   Feature #8: Data Refresh Animations
   ======================================== */
@keyframes valueUpdate {
    0% { 
        transform: scale(1);
        color: inherit;
    }
    50% { 
        transform: scale(1.08);
        filter: brightness(1.3);
    }
    100% { 
        transform: scale(1);
        color: inherit;
    }
}

.value-updated {
    animation: valueUpdate 0.6s ease-out;
}

/* Glow effect for updated values */
@keyframes glowPulse {
    0%, 100% { 
        box-shadow: 0 0 0 rgba(59, 130, 246, 0);
    }
    50% { 
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
    }
}

.value-glow {
    animation: glowPulse 1s ease-out;
}

/* ========================================
   Feature #3: Animated Weather Icons
   ======================================== */
@keyframes sunnyPulse {
    0%, 100% { 
        transform: scale(1);
        filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6));
    }
    50% { 
        transform: scale(1.1);
        filter: drop-shadow(0 0 15px rgba(251, 191, 36, 0.9));
    }
}

@keyframes rainFall {
    0%, 100% { 
        transform: translateY(0);
    }
    50% { 
        transform: translateY(4px);
    }
}

@keyframes cloudFloat {
    0%, 100% { 
        transform: translateX(0);
    }
    50% { 
        transform: translateX(3px);
    }
}

@keyframes stormShake {
    0%, 100% { transform: translateX(0) rotate(0deg); }
    25% { transform: translateX(-2px) rotate(-2deg); }
    75% { transform: translateX(2px) rotate(2deg); }
}

@keyframes snowDrift {
    0%, 100% { 
        transform: translateY(0) translateX(0);
    }
    33% { 
        transform: translateY(2px) translateX(-2px);
    }
    66% { 
        transform: translateY(-2px) translateX(2px);
    }
}

.weather-icon-sunny {
    animation: sunnyPulse 3s ease-in-out infinite;
}

.weather-icon-rain {
    animation: rainFall 1.5s ease-in-out infinite;
}

.weather-icon-cloud {
    animation: cloudFloat 4s ease-in-out infinite;
}

.weather-icon-storm {
    animation: stormShake 0.5s ease-in-out infinite;
}

.weather-icon-snow {
    animation: snowDrift 3s ease-in-out infinite;
}

/* ========================================
   Feature #7: Skeleton Loading States
   ======================================== */
@keyframes skeletonLoading {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

.skeleton {
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.05) 25%,
        rgba(255, 255, 255, 0.15) 50%,
        rgba(255, 255, 255, 0.05) 75%
    );
    background-size: 200% 100%;
    animation: skeletonLoading 1.5s ease-in-out infinite;
    border-radius: 0.5rem;
}

.skeleton-text {
    height: 1.2em;
    margin: 0.5em 0;
}

.skeleton-circle {
    border-radius: 50%;
}

.skeleton-rect {
    border-radius: 0.5rem;
}

/* Dark mode skeleton */
body.body--dark .skeleton {
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.03) 25%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 75%
    );
    background-size: 200% 100%;
}

/* Fade out skeleton when data loads */
.skeleton-fade-out {
    animation: fadeOut 0.4s ease-out forwards;
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}
"""

@ui.page('/')
def main_page():
    # Initialize theme
    ui.add_head_html(f"<style>{APP_CSS}</style>")
    ui.add_head_html(f"<style>{ThemeManager.get_css()}</style>")
    dark = ui.dark_mode(True)  # Default to dark mode
    
    # --- UI Element References (State) ---
    # These will be updated by the refresh logic
    state = {
        "temp": None, "cond": None, "icon": None, 
        "humidity": None, "wind": None, "updated": None,
        "feels": None, "pressure": None, "sunrise": None, "sunset": None, "rainfall": None,
        "hero_pressure": None, # Separate key for Hero card pressure
        # API specific state
        "api_temp": None, "api_cond": None, "api_icon": None, "api_humidity": None, "api_wind": None, "api_pressure": None,
        "chart": None, "humidity_chart": None, "pressure_chart": None, "rainfall_chart": None,
        "forecast_container": None,
        "iot_status": None, # New state
        "loading_screen": None, # Loading overlay
        "main_content": None, # Main content container
        "start_time": time.time() # For minimum loading duration
    }

    # --- Loading Screen ---
    with ui.element('div').classes('loading-screen') as loading_screen:
        state['loading_screen'] = loading_screen
        # Icon and text removed as requested, only loader remains
        ui.element('div').classes('loader')

    # --- Header (fades in with main content) ---
    with ui.header().classes('glass-header q-px-md h-auto py-2 flex items-center justify-between main-content fixed top-0 z-50') as header:
        # Left: City Name
        with ui.row().classes('items-center gap-2'):
            ui.icon('place', size='xs', color='blue-400')
            state['city_label'] = ui.label(CITY).classes('text-xl text-slate-700 dark:text-slate-200 font-bold')

        # Center: Title (Absolute)
        ui.label('Weather Prediction Model').classes('absolute left-1/2 -translate-x-1/2 text-2xl font-bold tracking-tight text-blue-500 dark:text-blue-400 z-10 text-center whitespace-nowrap')
        
        # Right: Controls
        with ui.row().classes('items-center gap-4'):
            # IoT Status
            with ui.row().classes('items-center gap-2 mr-2'):
                ui.icon('sensors', size='sm', color='slate-500')
                state['iot_status'] = ui.label('Checking...').classes('text-base font-bold text-slate-500')

            # Status indicator
            state['updated'] = ui.label('Syncing...').classes('text-base text-slate-600 dark:text-slate-500 mr-2')
            
            # Theme Toggle with dynamic icon
            def toggle_theme():
                dark.toggle()
                # Update icon based on new state
                if dark.value:
                    # Dark mode is ON, show sun (click to go light)
                    theme_btn.props('icon=light_mode')
                else:
                    # Light mode is ON, show moon (click to go dark)
                    theme_btn.props('icon=dark_mode')
            
            theme_btn = ui.button(icon='light_mode', on_click=toggle_theme).props('flat round dense')
            state['theme_btn'] = theme_btn
            with theme_btn:
                ui.tooltip('Toggle Theme')
            
            # Set initial icon based on dark mode state
            if dark.value:
                theme_btn.props('icon=light_mode')
            else:
                theme_btn.props('icon=dark_mode')
            
            with ui.button(icon='refresh', on_click=lambda: refresh_weather()).props('flat round dense'):
                ui.tooltip('Refresh Data')
            
            with ui.button(icon='auto_graph', on_click=lambda: ui.open(API_BASE + "/docs")).props('flat round dense'):
                ui.tooltip('API Docs')

    # --- Search Bar (Centered below header) ---
    with ui.row().classes('w-full max-w-md mx-auto mt-20 mb-[-3rem] z-40 relative justify-center'):
        # Container for input and results
        with ui.column().classes('w-full relative'):
            search_input = ui.input(placeholder='Search Location...').classes(
                'w-full glass-panel px-6 py-2 text-lg text-slate-200 focus:text-white transition-all rounded-full shadow-lg border border-white/10'
            ).props('rounded outlined dense input-class="text-center"')
            
            # Add search icon
            with search_input.add_slot('prepend'):
                ui.icon('search', color='blue-400').classes('ml-2')
            
            # Results dropdown (absolute positioned)
            results_container = ui.card().classes(
                'absolute top-full left-0 w-full mt-2 z-50 glass-panel p-0 overflow-hidden hidden transition-all duration-200'
            )
            
            def select_city(city_name):
                search_input.value = city_name
                results_container.classes(add='hidden')
                handle_search()

            async def update_suggestions(e):
                val = e.sender.value
                if len(val) < 3:
                    results_container.classes(add='hidden')
                    return
                
                try:
                    # Call search endpoint
                    loop = asyncio.get_running_loop()
                    results = await loop.run_in_executor(None, lambda: requests.get(API_BASE + f"/api/weatherapi/search?q={val}", timeout=2).json())
                    
                    results_container.clear()
                    if results:
                        results_container.classes(remove='hidden')
                        with results_container:
                            for res in results:
                                name = res.get("name")
                                region = res.get("region")
                                country = res.get("country")
                                full_name = f"{name}, {country}"
                                
                                with ui.item(on_click=lambda n=full_name: select_city(n)).classes('w-full hover:bg-white/10 cursor-pointer px-4 py-2 transition-colors'):
                                    with ui.row().classes('items-center justify-between w-full'):
                                        ui.label(name).classes('text-slate-200 font-medium')
                                        ui.label(country).classes('text-xs text-slate-400')
                    else:
                        results_container.classes(add='hidden')
                except Exception as ex:
                    print(f"Autocomplete error: {ex}")
                    results_container.classes(add='hidden')

            search_input.on('input', update_suggestions)
            
            def handle_search():
                city = search_input.value
                if not city: return
                
                results_container.classes(add='hidden')
                
                # Call API to update city
                try:
                    r = requests.post(API_BASE + "/api/settings/city", json={"city": city}, timeout=5)
                    if r.status_code == 200:
                        ui.notify(f"Location updated to {city}", type='positive')
                        search_input.value = "" # Clear input
                        refresh_weather()
                    else:
                        ui.notify(f"Error: {r.json().get('message')}", type='negative')
                except Exception as e:
                    ui.notify(f"Failed to update location: {str(e)}", type='negative')

            search_input.on('keydown.enter', handle_search)

    # --- Main Content (Dashboard) ---
    with ui.element('div').classes('w-full max-w-7xl mx-auto p-4 md:p-6 gap-6 flex flex-col main-content mt-16') as main_content:
        state['main_content'] = main_content
        
        # Feature #10: AI Weather Summary Card
        with ui.card().classes('glass-panel w-full px-5 py-4 no-shadow border-none'):
            with ui.row().classes('w-full items-center gap-4'):
                # Left: Icon
                state['summary_icon'] = ui.label('🌤️').classes('text-5xl')
                
                # Middle: Summary text
                with ui.column().classes('flex-1 gap-2'):
                    with ui.row().classes('items-center gap-2'):
                        ui.label('Weather Insights').classes('text-xl font-bold text-slate-700 dark:text-slate-200')
                        state['summary_status'] = ui.label('🟢').classes('text-base')
                    
                    state['summary_text'] = ui.label('Loading weather insights...').classes(
                        'text-lg text-slate-600 dark:text-slate-300 leading-relaxed'
                    )
                    
                    # Recommendations chips
                    state['recommendations_container'] = ui.row().classes('gap-2 flex-wrap')
        
        # Top Row: Hero + Details
        with ui.row().classes('w-full gap-6 flex-nowrap flex-col md:flex-row'):
            
            # 1. Hero Card (Split View: Sensor vs API)
            with ui.column().classes('glass-panel p-0 w-full md:w-7/12 justify-between relative overflow-hidden'):
                # Background accent blob
                ui.element('div').classes('absolute -top-10 -right-10 w-40 h-40 bg-blue-500 blur-[80px] opacity-20 rounded-full pointer-events-none')
                
                with ui.row().classes('w-full h-full flex-nowrap'):
                    # Left: Local Sensor
                    with ui.column().classes('w-1/2 p-6 border-r border-slate-200 dark:border-white/10 justify-between'):
                        with ui.column().classes('gap-0'):
                            ui.label('Local Sensor').classes('text-xs uppercase tracking-widest text-blue-500 dark:text-blue-400 font-bold')
                            state['cond'] = ui.label('—').classes('text-lg text-slate-700 dark:text-slate-200 mt-1 font-semibold leading-tight')
                        
                        state['icon'] = ui.label('—').classes('text-5xl filter drop-shadow-lg my-2')
                        
                        state['temp'] = ui.label('—').classes('text-6xl font-thin tracking-tighter text-slate-900 dark:text-white leading-none')
                        
                        with ui.column().classes('gap-2 mt-4 w-full'):
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('💧').classes('text-lg')
                                    ui.label('Humidity').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['humidity'] = ui.label('—%').classes('text-lg font-bold text-slate-700 dark:text-slate-200')
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('⏱️').classes('text-lg')
                                    ui.label('Pressure').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['hero_pressure'] = ui.label('— hPa').classes('text-lg font-bold text-slate-700 dark:text-slate-200')
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('🌧️').classes('text-lg')
                                    ui.label('Rain').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['rainfall'] = ui.label('— mm').classes('text-lg font-bold text-slate-700 dark:text-slate-200')

                    # Right: Weather API
                    with ui.column().classes('w-1/2 p-6 justify-between'):
                        with ui.column().classes('gap-0'):
                            ui.label('Weather API').classes('text-xs uppercase tracking-widest text-purple-500 dark:text-purple-400 font-bold')
                            state['api_cond'] = ui.label('—').classes('text-lg text-slate-700 dark:text-slate-200 mt-1 font-semibold leading-tight')
                        
                        state['api_icon'] = ui.label('—').classes('text-5xl filter drop-shadow-lg my-2')
                        
                        state['api_temp'] = ui.label('—').classes('text-6xl font-thin tracking-tighter text-slate-900 dark:text-white leading-none')
                        
                        with ui.column().classes('gap-2 mt-4 w-full'):
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('💧').classes('text-lg')
                                    ui.label('Humidity').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['api_humidity'] = ui.label('—%').classes('text-lg font-bold text-slate-700 dark:text-slate-200')
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('⏱️').classes('text-lg')
                                    ui.label('Pressure').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['api_pressure'] = ui.label('— hPa').classes('text-lg font-bold text-slate-700 dark:text-slate-200')
                            with ui.row().classes('items-center justify-between w-full'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label('💨').classes('text-lg')
                                    ui.label('Wind').classes('text-sm font-medium text-slate-500 dark:text-slate-400')
                                state['api_wind'] = ui.label('— kph').classes('text-lg font-bold text-slate-700 dark:text-slate-200')

            # 2. Details Grid (2x2)
            with ui.column().classes('w-full md:w-5/12 gap-4'):
                # Stats Grid - 2 columns, 2 rows
                with ui.grid().classes('w-full grid-cols-2 gap-4 h-full'):
                    
                    def detail_card(title, icon, color, with_sparkline=True):
                        with ui.column().classes('glass-panel p-5 justify-between h-full'):
                            with ui.row().classes('items-center gap-2 mb-2'):
                                ui.icon(icon, size='sm', color=color)
                                ui.label(title).classes('text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400 font-bold')
                            lbl = ui.label('—').classes('text-3xl font-bold text-slate-800 dark:text-slate-100 pl-1')
                            # Add sparkline container only if requested
                            if with_sparkline:
                                sparkline = ui.plotly({}).classes('w-full mt-2')
                                return lbl, sparkline
                            else:
                                return lbl, None

                    state['feels'], state['feels_sparkline'] = detail_card('Feels Like', 'thermostat', 'orange-400', with_sparkline=True)
                    state['pressure'], state['pressure_sparkline'] = detail_card('Pressure', 'speed', 'purple-400', with_sparkline=True)
                    state['sunrise'], _ = detail_card('Sunrise', 'wb_twilight', 'yellow-400', with_sparkline=False)
                    state['sunset'], _ = detail_card('Sunset', 'nightlight_round', 'indigo-400', with_sparkline=False)

        # 7-Day Forecast Section
        with ui.column().classes('w-full gap-4'):
            # Header with title and buttons
            with ui.column().classes('w-full gap-3 items-center'):
                ui.label('7-Day Forecast').classes('text-2xl font-bold text-slate-700 dark:text-slate-200')
                
                # Action Buttons (centered below title)
                with ui.row().classes('gap-3'):
                    def run_action(label, api_endpoint):
                        try:
                            ui.notify(f"Triggering {label}...", type='info')
                            r = requests.get(API_BASE + api_endpoint, timeout=10)
                            data = r.json()
                            msg = data.get("message") or "Action Complete"
                            if r.status_code == 200:
                                ui.notify(f"Success: {msg}", type='positive')
                            else:
                                ui.notify(f"Error: {msg}", type='negative')
                            refresh_weather()
                        except Exception as e:
                            ui.notify(f"Failed: {str(e)}", type='negative')

                    with ui.button("Trigger ML Forecast", on_click=lambda: run_action("ML Forecast", "/api/ml_forecast")).classes('glass-panel px-5 py-2.5 text-sm font-medium text-blue-600 dark:text-blue-200 hover:text-blue-800 dark:hover:text-white transition-colors'):
                        pass
                    with ui.button("Sync WeatherAPI", on_click=lambda: run_action("WeatherAPI Sync", "/api/weatherapi/sync")).classes('glass-panel px-5 py-2.5 text-sm font-medium text-blue-600 dark:text-blue-200 hover:text-blue-800 dark:hover:text-white transition-colors'):
                        pass
            
            # Forecast grid (centered)
            state['forecast_container'] = ui.row().classes('w-full flex-wrap gap-4 justify-center')

        # Charts Section - 4x1 Vertical Stack (Larger)
        with ui.grid().classes('w-full grid-cols-1 gap-6'):
            # Temperature Trend Chart
            with ui.card().classes('glass-panel w-full p-1 no-shadow border-none'):
                with ui.row().classes('w-full px-6 py-4 justify-between items-center'):
                     ui.label('Temperature Trend').classes('text-xl font-bold text-slate-700 dark:text-slate-200')
                state['chart'] = ui.plotly({}).classes('w-full h-80')
            
            # Humidity Trend Chart
            with ui.card().classes('glass-panel w-full p-1 no-shadow border-none'):
                with ui.row().classes('w-full px-6 py-4 justify-between items-center'):
                     ui.label('Humidity Trend').classes('text-xl font-bold text-slate-700 dark:text-slate-200')
                state['humidity_chart'] = ui.plotly({}).classes('w-full h-80')
            
            # Pressure Trend Chart
            with ui.card().classes('glass-panel w-full p-1 no-shadow border-none'):
                with ui.row().classes('w-full px-6 py-4 justify-between items-center'):
                     ui.label('Pressure Trend').classes('text-xl font-bold text-slate-700 dark:text-slate-200')
                state['pressure_chart'] = ui.plotly({}).classes('w-full h-80')
            
            # Rainfall Chart
            with ui.card().classes('glass-panel w-full p-1 no-shadow border-none'):
                with ui.row().classes('w-full px-6 py-4 justify-between items-center'):
                     ui.label('Rainfall').classes('text-xl font-bold text-slate-700 dark:text-slate-200')
                state['rainfall_chart'] = ui.plotly({}).classes('w-full h-80')



    # --- Logic: Refresh Function ---
    async def refresh_weather():
        """Fetches data and updates all UI elements"""
        # Visual loading indication
        state['updated'].set_text('Updating...')
        
        # Run blocking I/O in executor to avoid freezing UI during sleep
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, lambda: safe_get("/api/combined"))
        
        # Always hide loading screen after first attempt (success or failure)
        if state['loading_screen']:
            # Ensure minimum 3s duration
            elapsed = time.time() - state['start_time']
            remaining = 3 - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)

            try:
                # Check if not already hidden
                if 'hidden' not in str(state['loading_screen']._classes):
                    state['loading_screen']._classes.append('hidden')
                    state['loading_screen'].update()
            except Exception as e:
                print(f"[ui] Error hiding loading screen: {e}")
            
            # Clear reference so we don't delay subsequent refreshes
            state['loading_screen'] = None
        
        if not data:
            state['updated'].set_text('Offline')
            ui.notify('Could not fetch weather data', type='negative')
            return

        cur = data.get("current", {})
        sensor = data.get("sensor_data") or {}
        api = data.get("api_data") or {}
        
        # 1. Update Hero - Local Sensor
        if sensor:
            # Animate temperature update
            new_temp = _format_temp(sensor.get("temp"))
            if state['temp']._text != new_temp:
                state['temp'].classes.append('value-updated')
            state['temp'].set_text(new_temp)
            
            cond_text = sensor.get("condition") or "—"
            state['cond'].set_text(cond_text)
            
            emoji, color_cls, anim_cls = _get_weather_icon(cond_text)
            state['icon'].set_text(emoji)
            
            # Update icon classes with animation
            new_classes = f"text-5xl filter drop-shadow-lg my-2 {color_cls} {anim_cls}".split()
            try:
                state['icon'].classes.clear()
                state['icon'].classes.extend(new_classes)
            except:
                state['icon']._classes = new_classes
            state['icon'].update()

            hum = sensor.get("humidity")
            new_hum = f"{hum}%" if hum is not None else "—%"
            if state['humidity']._text != new_hum:
                state['humidity'].classes.append('value-updated')
            state['humidity'].set_text(new_hum)
            
            pres = sensor.get("pressure")
            pres_text = f"{pres} hPa" if pres is not None else "— hPa"
            if state['hero_pressure']._text != pres_text:
                state['hero_pressure'].classes.append('value-updated')
            state['hero_pressure'].set_text(pres_text)
            
            rain = sensor.get("rainfall")
            state['rainfall'].set_text(f"{rain:.1f} mm" if rain is not None else "— mm")
        else:
            state['temp'].set_text("—")
            state['cond'].set_text("No Sensor")
            state['icon'].set_text("📡")
            state['humidity'].set_text("—%")
            state['hero_pressure'].set_text("— hPa")
            state['rainfall'].set_text("— mm")

        # 1b. Update Hero - Weather API
        new_api_temp = _format_temp(api.get("temp"))
        if state['api_temp']._text != new_api_temp:
            state['api_temp'].classes.append('value-updated')
        state['api_temp'].set_text(new_api_temp)
        
        cond_api_text = api.get("condition") or "—"
        state['api_cond'].set_text(cond_api_text)
        
        emoji_api, color_cls_api, anim_cls_api = _get_weather_icon(cond_api_text)
        state['api_icon'].set_text(emoji_api)
        
        # Update API icon classes with animation
        new_classes_api = f"text-5xl filter drop-shadow-lg my-2 {color_cls_api} {anim_cls_api}".split()
        try:
            state['api_icon'].classes.clear()
            state['api_icon'].classes.extend(new_classes_api)
        except:
            state['api_icon']._classes = new_classes_api
        state['api_icon'].update()
        
        hum_api = api.get("humidity")
        state['api_humidity'].set_text(f"{hum_api}%" if hum_api is not None else "—%")
        
        pres_api = api.get("pressure")
        state['api_pressure'].set_text(f"{pres_api} hPa" if pres_api else "— hPa")
        
        wind_api = api.get("wind")
        state['api_wind'].set_text(f"{wind_api} kph" if wind_api else "— kph")

        state['updated'].set_text(f"Updated: {datetime.now().strftime('%H:%M')}")

        # 2. Update Details (Use API data for these as sensor might not have them)
        state['feels'].set_text(_format_temp(api.get("feels_like")))
        
        # Update pressure detail card (use sensor if available, otherwise API)
        if sensor and sensor.get("pressure"):
            pres_detail = sensor.get("pressure")
        else:
            pres_detail = api.get("pressure")
        
        new_pres_text = f"{pres_detail} hPa" if pres_detail else "— hPa"
        if state['pressure']._text != new_pres_text:
            state['pressure'].classes.append('value-updated')
        state['pressure'].set_text(new_pres_text)
        
        state['sunrise'].set_text(_format_time(api.get("sunrise")))
        state['sunset'].set_text(_format_time(api.get("sunset")))
        
        # 2b. Update Sparklines (Feature #4)
        from db.db import get_hourly_trends
        hourly_data = get_hourly_trends(hours=24)
        
        # Fallback to API forecast if DB is empty
        api_hourly = data.get("hourly_forecast", [])

        if not hourly_data.empty:
            # Feels Like sparkline (using temp as proxy)
            temp_data = hourly_data['avg_temp'].fillna(0).tolist()
            if temp_data:
                state['feels_sparkline'].update_figure(create_sparkline(temp_data, '#FB923C'))
            
            # Pressure sparkline
            pressure_data = hourly_data['avg_pressure'].fillna(0).tolist()
            if pressure_data:
                state['pressure_sparkline'].update_figure(create_sparkline(pressure_data, '#A855F7'))
        elif api_hourly:
            # Use API forecast
            temp_data = [h["temp"] for h in api_hourly]
            if temp_data:
                state['feels_sparkline'].update_figure(create_sparkline(temp_data, '#FB923C'))
            
            pressure_data = [h["pressure"] for h in api_hourly]
            if pressure_data:
                state['pressure_sparkline'].update_figure(create_sparkline(pressure_data, '#A855F7'))

        # 3. Update Charts
        update_chart(data)
        update_humidity_chart(data)
        update_pressure_chart(data)
        update_rainfall_chart(data)

        # 4. Update Forecast Strip
        daily = data.get("daily") or data.get("daily_forecast") or []
        build_forecast(daily)
        
        # 5. Update IoT Status
        iot_stat = data.get("sensor_status", "Unknown")
        state['iot_status'].set_text(iot_stat)
        # Update color based on status
        # We use the same list modification fix as before
        new_classes = ["text-base", "font-bold"]
        if iot_stat == "Connected":
            new_classes.append("text-green-400")
            
        # 6. Update City Name (if changed via API)
        city_name = data.get("city")
        if city_name and state.get('city_label'):
             state['city_label'].set_text(city_name)
        elif iot_stat == "Disconnected":
            new_classes.append("text-red-400")
        else:
            new_classes.append("text-slate-500")
            
        state['iot_status'].classes.clear()
        state['iot_status'].classes.extend(new_classes)
        state['iot_status'].update()
        
        # 6. Update AI Weather Summary (Feature #10)
        from services.weather_insights import generate_summary
        summary_data = generate_summary(
            current=cur,
            forecast=daily,
            sensor_status=iot_stat
        )
        
        # Update summary text
        state['summary_text'].set_text(summary_data['summary'])
        state['summary_status'].set_text(summary_data['status_emoji'])
        
        # Update icon based on condition
        if cur:
            cond = cur.get('condition', '')
            emoji, _, anim_cls = _get_weather_icon(cond)
            state['summary_icon'].set_text(emoji)
            if anim_cls:
                state['summary_icon'].classes.clear()
                state['summary_icon'].classes.extend(['text-5xl', anim_cls])
                state['summary_icon'].update()
        
        # Update recommendations chips
        state['recommendations_container'].clear()
        with state['recommendations_container']:
            for rec in summary_data['recommendations']:
                ui.chip(rec, color='blue').props('outline').classes(
                    'text-sm text-blue-600 dark:text-blue-300'
                )

    def update_chart(data):
        ch = data.get("chart", {}) or {}
        daily = data.get("daily") or []
        labels = ch.get("labels") or [d.get("day") for d in daily] or []
        
        # Data Series
        ai_data = ch.get("AI") or ch.get("ai") or []
        api_high = ch.get("API_high") or ch.get("api_high") or []
        api_low = ch.get("API_low") or ch.get("api_low") or []

        fig = go.Figure()

        # Add API bounds as a filled area (shows the range)
        if api_high and api_low:
            # Upper bound
            fig.add_trace(go.Scatter(
                x=labels, 
                y=api_high, 
                name="API High",
                line=dict(color='rgba(251, 146, 60, 0.5)', width=1),
                mode='lines',
                showlegend=True,
                hovertemplate='<b>API High</b><br>%{y:.1f}°C<extra></extra>'
            ))
            
            # Lower bound with fill
            fig.add_trace(go.Scatter(
                x=labels, 
                y=api_low, 
                name="API Low",
                line=dict(color='rgba(251, 146, 60, 0.5)', width=1),
                mode='lines',
                fill='tonexty',  # Fill to previous trace (API High)
                fillcolor='rgba(251, 146, 60, 0.15)',
                showlegend=True,
                hovertemplate='<b>API Low</b><br>%{y:.1f}°C<extra></extra>'
            ))
            
        # Add AI prediction line (prominent)
        if ai_data:
            fig.add_trace(go.Scatter(
                x=labels, 
                y=ai_data, 
                name="AI Prediction",
                line=dict(color='#3B82F6', width=3, shape='spline'),
                connectgaps=True,
                mode='lines+markers',
                marker=dict(
                    size=10, 
                    color='#3B82F6',
                    line=dict(width=2, color='#FFFFFF')
                ),
                showlegend=True,
                hovertemplate='<b>AI Prediction</b><br>%{y:.1f}°C<extra></extra>'
            ))

        # Layout Styling
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#64748b", size=12),
            margin=dict(l=50, r=30, t=30, b=50),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.05)',
                bordercolor='rgba(255,255,255,0.1)',
                borderwidth=1,
                font=dict(size=11)
            ),
            xaxis=dict(
                showgrid=False, 
                showline=True, 
                linecolor='rgba(100, 116, 139, 0.2)',
                tickfont=dict(size=11),
                title=dict(text="Date", font=dict(size=12))
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(100, 116, 139, 0.1)', 
                zeroline=False,
                tickfont=dict(size=11),
                title=dict(text="Temperature (°C)", font=dict(size=12))
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="rgba(15, 23, 42, 0.9)",
                font_size=12,
                font_family="Inter"
            )
        )
        state['chart'].update_figure(fig)

    def update_humidity_chart(data):
        ch = data.get("chart", {}) or {}
        labels = ch.get("labels") or []
        humidity_data = ch.get("humidity") or []
        
        fig = go.Figure()
        
        # Add humidity line
        if any(h is not None for h in humidity_data):
            fig.add_trace(go.Scatter(
                x=labels,
                y=humidity_data,
                name="Humidity",
                line=dict(color='#14B8A6', width=3, shape='spline'),
                connectgaps=True,
                mode='lines+markers',
                marker=dict(size=8, color='#14B8A6', line=dict(width=2, color='#FFFFFF')),
                hovertemplate='<b>Humidity</b><br>%{y:.0f}%<extra></extra>'
            ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#64748b", size=11),
            margin=dict(l=40, r=20, t=10, b=40),
            showlegend=False,
            xaxis=dict(showgrid=False, showline=True, linecolor='rgba(100, 116, 139, 0.2)', tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='rgba(100, 116, 139, 0.1)', zeroline=False, tickfont=dict(size=10), title=dict(text="%", font=dict(size=11))),
            hovermode="x unified"
        )
        state['humidity_chart'].update_figure(fig)

    def update_pressure_chart(data):
        ch = data.get("chart", {}) or {}
        labels = ch.get("labels") or []
        pressure_data = ch.get("pressure") or []
        
        fig = go.Figure()
        
        # Add pressure line
        if any(p is not None for p in pressure_data):
            fig.add_trace(go.Scatter(
                x=labels,
                y=pressure_data,
                name="Pressure",
                line=dict(color='#A855F7', width=3, shape='spline'),
                connectgaps=True,
                mode='lines+markers',
                marker=dict(size=8, color='#A855F7', line=dict(width=2, color='#FFFFFF')),
                hovertemplate='<b>Pressure</b><br>%{y:.0f} hPa<extra></extra>'
            ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#64748b", size=11),
            margin=dict(l=40, r=20, t=10, b=40),
            showlegend=False,
            xaxis=dict(showgrid=False, showline=True, linecolor='rgba(100, 116, 139, 0.2)', tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='rgba(100, 116, 139, 0.1)', zeroline=False, tickfont=dict(size=10), title=dict(text="hPa", font=dict(size=11))),
            hovermode="x unified"
        )
        state['pressure_chart'].update_figure(fig)

    def update_rainfall_chart(data):
        ch = data.get("chart", {}) or {}
        labels = ch.get("labels") or []
        rainfall_data = ch.get("rainfall") or []
        
        fig = go.Figure()
        
        # Add rainfall bars
        fig.add_trace(go.Bar(
            x=labels,
            y=rainfall_data,
            name="Rainfall",
            marker=dict(color='#06B6D4', line=dict(width=0)),
            hovertemplate='<b>Rainfall</b><br>%{y:.1f} mm<extra></extra>'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#64748b", size=11),
            margin=dict(l=40, r=20, t=10, b=40),
            showlegend=False,
            xaxis=dict(showgrid=False, showline=True, linecolor='rgba(100, 116, 139, 0.2)', tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor='rgba(100, 116, 139, 0.1)', zeroline=False, tickfont=dict(size=10), title=dict(text="mm", font=dict(size=11))),
            hovermode="x unified"
        )
        state['rainfall_chart'].update_figure(fig)

    def build_forecast(daily_data):
        container = state['forecast_container']
        container.clear()
        
        if not daily_data:
            with container:
                ui.label("No forecast available").classes("text-slate-500 italic")
            return

        with container:
            for day in daily_data:
                # Extract data
                date_str = day.get("day") or day.get("date", "—")
                try:
                    # Convert "2023-10-25" to "Wed"
                    dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    day_name = dt_obj.strftime("%a")
                    date_num = dt_obj.strftime("%d")
                except:
                    day_name = date_str[:3]
                    date_num = ""


                hi = day.get("high") or day.get("temp_high_c")
                lo = day.get("low") or day.get("temp_low_c")
                cond = day.get("cond") or day.get("condition")
                emoji, _, anim_cls = _get_weather_icon(cond)

                # Render Card
                with ui.column().classes('glass-panel p-5 items-center min-w-[110px] hover:bg-slate-100/20 dark:hover:bg-white/5 transition-colors cursor-pointer gap-2'):
                    ui.label(day_name).classes('font-bold text-base text-blue-600 dark:text-blue-200')
                    ui.label(date_num).classes('text-xs text-slate-500 mb-1')
                    ui.label(emoji).classes(f'text-4xl my-2 {anim_cls}')
                    ui.label(_format_temp(hi)).classes('text-xl font-bold text-slate-900 dark:text-white')
                    ui.label(_format_temp(lo)).classes('text-base text-slate-600 dark:text-slate-400')


    # (Action buttons moved to forecast section above)

    # Initial Fetch
    ui.timer(0.1, refresh_weather, once=True)
    ui.timer(REFRESH_SECONDS, refresh_weather)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="WeatherAI Dashboard", host="0.0.0.0", port=8080, reload=True)