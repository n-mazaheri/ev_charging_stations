import sqlite3
import pandas as pd
from pathlib import Path

# ============================
# CONFIG
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # project root
DATA_DIR = BASE_DIR / "data"
DB_FILE = BASE_DIR / "ev_charging.db"

CHARGING_CSV = DATA_DIR / "ev_stations.csv"
REVIEWS_CSV = DATA_DIR / "user_reviews.csv"

# ============================
# LOAD CSV FILES
# ============================
charging_df = pd.read_csv(CHARGING_CSV)
reviews_df = pd.read_csv(REVIEWS_CSV)

# ============================
# CLEAN COLUMN NAMES
# ============================
# Convert spaces to underscores, lowercase, and strip
charging_df.columns = [c.strip().replace(" ", "_").lower() for c in charging_df.columns]
reviews_df.columns = [c.strip().replace(" ", "_").lower() for c in reviews_df.columns]

# ============================
# CONNECT TO SQLITE
# ============================
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# ============================
# CREATE TABLES
# ============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS charging_stations (
    station_id INTEGER PRIMARY KEY,
    provider TEXT,
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    charging_speed TEXT,
    available_chargers INTEGER,
    charging_types TEXT,
    accessibility TEXT,
    operating_hours TEXT,
    avg_sentiment REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_reviews (
    review_id INTEGER PRIMARY KEY,
    user_id TEXT,
    station_id INTEGER,
    preferred_charging_speed TEXT,
    preferred_charging_type TEXT,
    feedback TEXT,
    sentiment REAL,
    FOREIGN KEY(station_id) REFERENCES charging_stations(station_id)
)
""")

conn.commit()

# ============================
# INSERT DATA INTO TABLES
# ============================
charging_df.to_sql("charging_stations", conn, if_exists="replace", index=False)
reviews_df.to_sql("user_reviews", conn, if_exists="replace", index=False)

# ============================
# FIND UNIQUE VALUES FOR SELECTED COLUMNS
# ============================
def print_unique_values(df, columns, title):
    print(f"\n=== Unique values for {title} ===")
    for col in columns:
        if col in df.columns:
            uniques = df[col].dropna().unique().tolist()
            print(f"{col}: {uniques}")
        else:
            print(f"{col}: [Column not found]")

charging_columns = ["provider", "location_name", "charging_speed", "charging_types", "accessibility"]
print_unique_values(charging_df, charging_columns, "Charging Stations")

# ============================
# CLOSE CONNECTION
# ============================
conn.close()
print("\n✅ Database created and data inserted at", DB_FILE)
