import os
import pandas as pd
import sqlite3
from generate_sample_data import generate_sample_data
from api.train_ml_model import train_model

def export_db_to_csv():
    """Exports reading data from DB to raw_data.csv for training."""
    print("📦 Exporting database to raw_data.csv...")
    
    # Connect to DB
    db_path = os.path.join("db", "weather_data.db")
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
        
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM readings ORDER BY timestamp ASC", con)
    con.close()
    
    if df.empty:
        print("⚠️ Database is empty. No data to export.")
        return False
        
    # Save to CSV
    df.to_csv("raw_data.csv", index=False)
    print(f"✅ Exported {len(df)} rows to raw_data.csv")
    return True

def main():
    print("🚀 Starting ML Setup...")
    
    # 1. Generate Sample Data (if DB is empty or missing)
    # We'll run it anyway to ensure we have enough data for training
    print("\n[Step 1/3] Generating Sample Data...")
    generate_sample_data(days=14, readings_per_day=24) # Generate 2 weeks of data
    
    # 2. Export to CSV
    print("\n[Step 2/3] Preparing Training Data...")
    if not export_db_to_csv():
        print("❌ Failed to prepare data. Aborting.")
        return
        
    # 3. Train Model
    print("\n[Step 3/3] Training ML Model...")
    train_model()
    
    print("\n✨ Setup Complete! You should now see 7-day forecasts.")

if __name__ == "__main__":
    main()
