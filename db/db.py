import sqlite3
from pathlib import Path
# import pandas as pd # Moved to lazy import
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent / "weather_data.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    temperature_c REAL,
    humidity_perc REAL,
    pressure_hpa REAL,
    rainfall_mm REAL,
    status TEXT
);

CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    source TEXT,
    day_index INTEGER,
    day_date TEXT,
    temp_high_c REAL,
    temp_low_c REAL,
    rain_prob_perc REAL,
    condition TEXT,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    alert_type TEXT,
    message TEXT
);
"""

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(SCHEMA)
    con.commit()
    con.close()

def insert_reading(r):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO readings (timestamp,temperature_c,humidity_perc,pressure_hpa,rainfall_mm,status)
    VALUES (?,?,?,?,?,?)
    """, (r["timestamp"], r["temperature_c"], r["humidity_perc"], r["pressure_hpa"], r["rainfall_mm"], r["status"]))
    con.commit()
    con.close()

def insert_forecast_batch(source, created_at, forecast_list, summary=None):
    """
    Insert a batch of 7-day forecasts. Avoid duplicate batches by the caller if needed.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for idx, d in enumerate(forecast_list, start=1):
        cur.execute("""
        INSERT INTO forecasts (created_at,source,day_index,day_date,temp_high_c,temp_low_c,rain_prob_perc,condition,summary)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            created_at, source, idx,
            d.get("day"),
            d.get("temp_high_c"),
            d.get("temp_low_c"),
            d.get("rain_prob_perc"),
            d.get("condition"),
            summary
        ))
    con.commit()
    con.close()

def get_latest_reading(limit=1):
    import pandas as pd
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM readings ORDER BY timestamp DESC LIMIT {limit}",
        con, parse_dates=["timestamp"]
    )
    con.close()
    return df

def get_daily_trends(days=7):
    """Get daily aggregated data for trend charts."""
    try:
        import pandas as pd
        con = sqlite3.connect(DB_PATH)
        # Get data from last N days, group by date
        query = f"""
        SELECT 
            DATE(timestamp) as date,
            AVG(temperature_c) as avg_temp,
            AVG(humidity_perc) as avg_humidity,
            AVG(pressure_hpa) as avg_pressure,
            SUM(rainfall_mm) as total_rainfall
        FROM readings
        WHERE timestamp >= datetime('now', '-{days} days')
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
        """
        df = pd.read_sql_query(query, con)
        con.close()
        return df
    except Exception as e:
        print(f"Error getting daily trends: {e}")
        return pd.DataFrame()

def get_hourly_trends(hours=24):
    """Get hourly data for sparkline charts."""
    try:
        import pandas as pd
        con = sqlite3.connect(DB_PATH)
        query = f"""
        SELECT 
            strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
            AVG(temperature_c) as avg_temp,
            AVG(humidity_perc) as avg_humidity,
            AVG(pressure_hpa) as avg_pressure,
            SUM(rainfall_mm) as total_rainfall
        FROM readings
        WHERE timestamp >= datetime('now', '-{hours} hours')
        GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp)
        ORDER BY hour ASC
        """
        df = pd.read_sql_query(query, con)
        con.close()
        return df
    except Exception as e:
        print(f"Error getting hourly trends: {e}")
        return pd.DataFrame()

def query_readings():
    import pandas as pd
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM readings ORDER BY timestamp ASC", con, parse_dates=["timestamp"])
    con.close()
    return df

def get_forecasts():
    import pandas as pd
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM forecasts ORDER BY created_at DESC", con, parse_dates=["created_at"])
    con.close()
    return df

def insert_alert(t, msg):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO alerts (created_at,alert_type,message) VALUES (?,?,?)",
                (datetime.now().isoformat(), t, msg))
    con.commit()
    con.close()

# -------------------------
# Utility helpers (no schema change)
# -------------------------
def get_last_forecast_time_for_source(source):
    """
    Returns a datetime or None for the most recent forecast 'created_at' for a source.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT created_at FROM forecasts WHERE source=? ORDER BY created_at DESC LIMIT 1", (source,))
    row = cur.fetchone()
    con.close()
    if not row:
        return None
    try:
        return datetime.fromisoformat(row[0])
    except:
        return None

def cleanup_old_readings(days=30):
    """
    Delete readings older than `days`. Returns number of deleted rows.
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM readings WHERE timestamp < ?", (cutoff,))
    deleted = cur.rowcount
    con.commit()
    con.close()
    return deleted

def cleanup_old_forecasts(days=30):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM forecasts WHERE created_at < ?", (cutoff,))
    deleted = cur.rowcount
    con.commit()
    con.close()
    return deleted

def cleanup_old_alerts(days=90):
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM alerts WHERE created_at < ?", (cutoff,))
    deleted = cur.rowcount
    con.commit()
    con.close()
    return deleted
