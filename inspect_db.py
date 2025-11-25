
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.getcwd(), "db", "weather_data.db")

def inspect_bad_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # Check for rainfall > 100mm (arbitrary high threshold for a single reading)
        query = "SELECT * FROM readings WHERE rainfall_mm > 100 ORDER BY rainfall_mm DESC LIMIT 20"
        df = pd.read_sql_query(query, conn)
        
        print(f"Found {len(df)} records with rainfall > 100mm:")
        print(df)
        
        # Count total bad records
        count = conn.execute("SELECT COUNT(*) FROM readings WHERE rainfall_mm > 100").fetchone()[0]
        print(f"\nTotal records with rainfall > 100mm: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_bad_data()
