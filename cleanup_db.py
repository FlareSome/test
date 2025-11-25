
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "db", "weather_data.db")

def cleanup_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # Count before
        count_before = conn.execute("SELECT COUNT(*) FROM readings WHERE rainfall_mm > 50").fetchone()[0]
        print(f"Found {count_before} records with rainfall > 50mm.")

        if count_before > 0:
            # Update bad records to 0.0
            # We assume > 50mm is definitely an error given the sensor context
            cursor = conn.execute("UPDATE readings SET rainfall_mm = 0.0 WHERE rainfall_mm > 50")
            print(f"Updated {cursor.rowcount} records.")
            conn.commit()
            print("Cleanup successful.")
        else:
            print("No bad records found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_data()
