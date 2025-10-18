import requests
from typing import Optional
import os

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

def geocode_city(city_name: str) -> Optional[tuple[float, float]]:
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": city_name, "key": OPENCAGE_API_KEY, "limit": 1}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lng = data["results"][0]["geometry"]["lng"]
            print("lat and len is ", lat, len)
            return lat, lng
    
    return None
