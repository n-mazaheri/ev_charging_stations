from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    charging_speed: Optional[str] = None
    charging_type: Optional[str] = None
    accessibility: Optional[str] = None

class StationOutput(BaseModel):
    station_id: int
    provider: str
    location_name: str
    latitude: float
    longitude: float
    charging_speed: str
    available_chargers: int
    charging_types: str
    accessibility: str
    operating_hours: str
    avg_sentiment: Optional[float]
    num_reviews: Optional[int]
