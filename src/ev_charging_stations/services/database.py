import sqlite3
from pathlib import Path
from typing import List
from src.ev_charging_stations.models.query_models import StationOutput
import math

# Path to your DB (adjust if needed)
DB_FILE = Path(__file__).resolve().parent.parent.parent.parent / "ev_charging.db"

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points"""
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_stations(filters: dict, initial_radius=20, max_radius=600, step=30) -> List[StationOutput]:
    """
    Find stations matching filters. If no results, expand search radius incrementally.
    """

    DB_FILE = Path(__file__).resolve().parent.parent.parent.parent / "ev_charging.db"

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = "SELECT * FROM charging_stations WHERE 1=1"
    params = []

    if filters.get("charging_speed"):
        query += " AND charging_speed = ?"
        params.append(filters["charging_speed"])

    if filters.get("charging_type"):
        query += " AND charging_types = ?"
        params.append(filters["charging_type"])

    if filters.get("accessibility"):
        query += " AND accessibility = ?"
        params.append(filters["accessibility"])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    stations = [
        StationOutput(
            station_id=row[columns.index("station_id")],
            provider=row[columns.index("provider")],
            location_name=row[columns.index("location_name")],
            latitude=row[columns.index("latitude")],
            longitude=row[columns.index("longitude")],
            charging_speed=row[columns.index("charging_speed")],
            available_chargers=row[columns.index("available_chargers")],
            charging_types=row[columns.index("charging_types")],
            accessibility=row[columns.index("accessibility")],
            operating_hours=row[columns.index("operating_hours")],
            avg_sentiment=row[columns.index("avg_sentiment")] if "avg_sentiment" in columns else None,
            num_reviews=row[columns.index("num_reviews")] if "num_reviews" in columns else None
        )
        for row in rows
    ]

    if filters.get("latitude") and filters.get("longitude"):
        user_lat = filters["latitude"]
        user_lon = filters["longitude"]
        radius = initial_radius

        filtered = []
        while radius <= max_radius and not filtered:
            filtered = [
                s for s in stations
                if s.latitude is not None and s.longitude is not None and
                   haversine(user_lat, user_lon, s.latitude, s.longitude) <= radius
            ]
            if not filtered:
                radius += step  # expand radius
        stations = filtered
    if filters.get("sort_by_reviews"):
        stations.sort(
            key=lambda s: ((s.avg_sentiment or 0), (s.num_reviews or 0)),
            reverse=True
        )

    conn.close()
    return stations

