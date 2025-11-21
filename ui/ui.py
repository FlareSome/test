# ui/ui.py
# Modern Glassmorphism Weather Dashboard
from nicegui import ui
import requests
import os
import sys
from datetime import datetime
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.theme_manager import ThemeManager

# --- Configuration ---
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
CITY = os.getenv("CITY_NAME", "New Town, West Bengal")
REFRESH_SECONDS = 300  # Increased to 5 mins to be polite to APIs, but adjustable

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
    """Returns a tuple (Emoji, CSS Class for animation/color)"""
    cond = (cond or "").lower()
    if "storm" in cond or "thunder" in cond: return "⛈️", "text-yellow-300"
    if "rain" in cond or "drizzle" in cond: return "🌧️", "text-blue-300"
    if "snow" in cond or "sleet" in cond: return "❄️", "text-white"
    if "clear" in cond or "sun" in cond: return "☀️", "text-orange-300"
    if "partly" in cond: return "🌤️", "text-yellow-100"
    if "cloud" in cond or "overcast" in cond: return "☁️", "text-gray-300"
    if "fog" in cond or "mist" in cond: return "🌫️", "text-gray-400"
    return "🌡️", "text-blue-200"

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
}

/* Custom Scrollbar for horizontal lists */
.hide-scroll::-webkit-scrollbar {
    height: 6px;
}
.hide-scroll::-webkit-scrollbar {
    border-radius: 10px;
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
        "chart": None, "humidity_chart": None, "pressure_chart": None, "rainfall_chart": None,
        "forecast_container": None,
        "iot_status": None # New state
    }

    # --- Header ---
    with ui.header().classes('glass-header q-px-md h-16 flex items-center justify-between'):
        with ui.row().classes('items-center gap-2'):
            ui.label('WeatherAI').classes('text-xl font-bold tracking-tight text-blue-400')
            ui.label(f'• {CITY}').classes('text-sm text-slate-600 dark:text-slate-400 font-medium')
        
        with ui.row().classes('items-center gap-3'):
            # IoT Status
            with ui.row().classes('items-center gap-1 mr-2'):
                ui.icon('sensors', size='xs', color='slate-500')
                state['iot_status'] = ui.label('Checking...').classes('text-xs font-bold text-slate-500')

            # Status indicator
            state['updated'] = ui.label('Syncing...').classes('text-xs text-slate-600 dark:text-slate-500 mr-2')
            
            # Theme Toggle
            with ui.button(icon='dark_mode', on_click=dark.toggle).props('flat round dense'):
                ui.tooltip('Toggle Theme')
            
            with ui.button(icon='refresh', on_click=lambda: refresh_weather()).props('flat round dense'):
                ui.tooltip('Refresh Data')
            
            with ui.button(icon='auto_graph', on_click=lambda: ui.open(API_BASE + "/docs")).props('flat round dense'):
                ui.tooltip('API Docs')

    # --- Main Content ---
    with ui.element('div').classes('w-full max-w-7xl mx-auto p-4 md:p-6 gap-6 flex flex-col'):
        
        # Top Row: Hero + Details
        with ui.row().classes('w-full gap-6 flex-nowrap flex-col md:flex-row'):
            
            # 1. Hero Card (Current Weather) - with Rainfall
            with ui.column().classes('glass-panel p-8 w-full md:w-5/12 justify-between relative overflow-hidden'):
                # Background accent blob
                ui.element('div').classes('absolute -top-10 -right-10 w-40 h-40 bg-blue-500 blur-[80px] opacity-20 rounded-full pointer-events-none')
                
                with ui.row().classes('w-full justify-between items-start'):
                    with ui.column().classes('gap-0'):
                        ui.label('Now').classes('text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 font-bold')
                        state['cond'] = ui.label('—').classes('text-2xl text-slate-700 dark:text-slate-200 mt-1 font-semibold')
                    state['icon'] = ui.label('—').classes('text-6xl filter drop-shadow-lg')
                
                with ui.row().classes('items-baseline gap-1 mt-4'):
                    state['temp'] = ui.label('—').classes('text-8xl font-thin tracking-tighter text-slate-900 dark:text-white leading-none')

                # Bottom row: Rainfall, Humidity, Wind (all in one row)
                with ui.row().classes('w-full justify-between mt-6 pt-6 border-t border-slate-200 dark:border-white/10'):
                    with ui.row().classes('items-center gap-1'):
                        ui.label('🌧️').classes('text-base')
                        state['rainfall'] = ui.label('Rain: — mm').classes('text-base text-slate-600 dark:text-slate-300 font-medium')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('💧').classes('text-base')
                        state['humidity'] = ui.label('Humidity: —%').classes('text-base text-slate-600 dark:text-slate-300 font-medium')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('💨').classes('text-base')
                        state['wind'] = ui.label('Wind: — kph').classes('text-base text-slate-600 dark:text-slate-300 font-medium')

            # 2. Details Grid (2x2)
            with ui.column().classes('w-full md:w-7/12 gap-4'):
                # Stats Grid - 2 columns, 2 rows
                with ui.grid().classes('w-full grid-cols-2 gap-4 h-full'):
                    
                    def detail_card(title, icon, color):
                        with ui.column().classes('glass-panel p-5 justify-center h-full'):
                            with ui.row().classes('items-center gap-2 mb-2'):
                                ui.icon(icon, size='sm', color=color)
                                ui.label(title).classes('text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400 font-bold')
                            lbl = ui.label('—').classes('text-3xl font-bold text-slate-800 dark:text-slate-100 pl-1')
                            return lbl

                    state['feels'] = detail_card('Feels Like', 'thermostat', 'orange-400')
                    state['pressure'] = detail_card('Pressure', 'speed', 'purple-400')
                    state['sunrise'] = detail_card('Sunrise', 'wb_twilight', 'yellow-400')
                    state['sunset'] = detail_card('Sunset', 'nightlight_round', 'indigo-400')

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

        # Charts Section - 2x2 Grid (Larger)
        with ui.grid().classes('w-full grid-cols-1 md:grid-cols-2 gap-4'):
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
    def refresh_weather():
        """Fetches data and updates all UI elements"""
        # Visual loading indication
        state['updated'].set_text('Updating...')
        
        data = safe_get("/api/combined")
        
        if not data:
            state['updated'].set_text('Offline')
            ui.notify('Could not fetch weather data', type='negative')
            return

        cur = data.get("current", {})
        
        # 1. Update Hero
        state['temp'].set_text(_format_temp(cur.get("temp")))
        
        cond_text = cur.get("condition") or cur.get("cond") or "—"
        state['cond'].set_text(cond_text)
        
        emoji, color_cls = _get_weather_icon(cond_text)
        state['icon'].set_text(emoji)
        
        # Update icon classes safely
        # state['icon'].classes is a list, so we modify it in place
        new_classes = f"text-6xl filter drop-shadow-lg {color_cls}".split()
        try:
            state['icon'].classes.clear()
            state['icon'].classes.extend(new_classes)
        except Exception:
            # Fallback if classes is not a list (e.g. older nicegui)
            state['icon']._classes = new_classes
            
        state['icon'].update()

        hum = cur.get("humidity")
        state['humidity'].set_text(f"Humidity: {hum}%" if hum else "Humidity: —%")
        
        wind = cur.get("wind")
        state['wind'].set_text(f"Wind: {wind} kph" if wind else "Wind: — kph")
        state['updated'].set_text(f"Updated: {datetime.now().strftime('%H:%M')}")

        # 2. Update Details
        state['feels'].set_text(_format_temp(cur.get("feels_like")))
        pres = cur.get("pressure")
        state['pressure'].set_text(f"{pres} hPa" if pres else "—")
        rain = cur.get("rainfall")
        state['rainfall'].set_text(f"Rain: {rain:.1f} mm" if rain is not None else "Rain: — mm")
        state['sunrise'].set_text(_format_time(cur.get("sunrise")))
        state['sunset'].set_text(_format_time(cur.get("sunset")))

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
        new_classes = ["text-xs", "font-bold"]
        if iot_stat == "Connected":
            new_classes.append("text-green-400")
        elif iot_stat == "Disconnected":
            new_classes.append("text-red-400")
        else:
            new_classes.append("text-slate-500")
            
        state['iot_status'].classes.clear()
        state['iot_status'].classes.extend(new_classes)
        state['iot_status'].update()

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
                emoji, _ = _get_weather_icon(cond)

                # Render Card
                with ui.column().classes('glass-panel p-5 items-center min-w-[110px] hover:bg-slate-100/20 dark:hover:bg-white/5 transition-colors cursor-pointer gap-2'):
                    ui.label(day_name).classes('font-bold text-base text-blue-600 dark:text-blue-200')
                    ui.label(date_num).classes('text-xs text-slate-500 mb-1')
                    ui.label(emoji).classes('text-4xl my-2')
                    ui.label(_format_temp(hi)).classes('text-xl font-bold text-slate-900 dark:text-white')
                    ui.label(_format_temp(lo)).classes('text-base text-slate-600 dark:text-slate-400')

    # (Action buttons moved to forecast section above)

    # Initial Fetch
    ui.timer(0.1, refresh_weather, once=True)
    ui.timer(REFRESH_SECONDS, refresh_weather)

ui.run(title="WeatherAI Dashboard", host="0.0.0.0", port=8080, reload=True)