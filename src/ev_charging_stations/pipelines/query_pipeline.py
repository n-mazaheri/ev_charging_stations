from src.ev_charging_stations.services.llm_extraction import parse_user_question
from src.ev_charging_stations.services.geocoding import geocode_city
from src.ev_charging_stations.services.database import find_stations
from fastapi import HTTPException

def run_query_pipeline(user_question: str):
    # Step 1: Parse with LLM
    filters = parse_user_question(user_question)

    # Step 1b: Handle API failure
    if filters is None:
        raise HTTPException(
            status_code=500,
            detail="Error: Failed to process query using language model. Please try again later."
        )

    # Step 2: If city provided but no lat/lng, geocode it
    if filters.city and not filters.latitude and not filters.longitude:
        lat_lng = geocode_city(filters.city)
        if lat_lng:
            filters.latitude, filters.longitude = lat_lng

    # Step 3: Prepare filter dict
    filter_dict = filters.dict(exclude_none=True)

    # Step 4: Query database
    stations = find_stations(filter_dict)

    return stations

