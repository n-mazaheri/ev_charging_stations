import sqlite3
from pathlib import Path
import pandas as pd
from textblob import TextBlob

# ============================
# CONFIG
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # project root
DB_FILE = BASE_DIR / "ev_charging.db"

# ============================
# CONNECT TO DATABASE
# ============================
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print(f"Connected to database at {DB_FILE}")

# ============================
# ADD SENTIMENT COLUMNS IF NEEDED
# ============================
def add_column_if_not_exists(table: str, column: str, col_type: str):
    cursor.execute(f"PRAGMA table_info({table})")
    existing_cols = [info[1] for info in cursor.fetchall()]
    if column not in existing_cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"✅ Added column '{column}' to '{table}' table.")
    else:
        print(f"⚠️ Column '{column}' already exists in '{table}' table.")

add_column_if_not_exists("user_reviews", "sentiment_score", "REAL")
add_column_if_not_exists("charging_stations", "avg_sentiment", "REAL")
add_column_if_not_exists("charging_stations", "num_reviews", "INTEGER")
conn.commit()

# ============================
# LOAD USER REVIEWS
# ============================
reviews_df = pd.read_sql_query("SELECT * FROM user_reviews", conn)

if reviews_df.empty:
    print("⚠️ No reviews found in the database.")
    conn.close()
    exit()

print(f"Found {len(reviews_df)} user reviews.")

# ============================
# COMPUTE SENTIMENT USING TEXTBLOB
# ============================
def get_sentiment_score(text):
    try:
        if not isinstance(text, str) or not text.strip():
            return None
        polarity = TextBlob(text).sentiment.polarity  # -1 to +1
        return round(polarity, 4)
    except Exception as e:
        print(f"Error analyzing: {text[:30]}... ({e})")
        return None

print("Computing sentiment scores...")
reviews_df["sentiment_score"] = reviews_df["feedback"].apply(get_sentiment_score)

# ============================
# UPDATE DATABASE WITH SCORES
# ============================
for _, row in reviews_df.iterrows():
    cursor.execute(
        "UPDATE user_reviews SET sentiment_score = ? WHERE review_id = ?",
        (row["sentiment_score"], row["review_id"])
    )

conn.commit()
print("✅ Updated sentiment scores in user_reviews table.")

# ============================
# COMPUTE AVERAGE SENTIMENT PER STATION
# ============================
avg_df = (
    reviews_df.groupby("station_id")["sentiment_score"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "avg_sentiment", "count": "num_reviews"})
)

for _, row in avg_df.iterrows():
    cursor.execute(
        """
        UPDATE charging_stations
        SET avg_sentiment = ?, num_reviews = ?
        WHERE station_id = ?
        """,
        (row["avg_sentiment"], row["num_reviews"], row["station_id"])
    )

# ============================
# SHOW FIRST 10 ROWS OF CHARGING STATIONS
# ============================
stations_df = pd.read_sql_query("SELECT * FROM charging_stations", conn)

print("\n🔹 First 10 rows of charging_stations table:")
print(stations_df.head(10))

conn.commit()
conn.close()

print("\n🎉 Sentiment analysis complete!")
print(f"Updated {len(avg_df)} stations with average sentiment scores.")
