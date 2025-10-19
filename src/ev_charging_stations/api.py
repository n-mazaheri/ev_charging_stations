"""Module for hosting the UI and API."""

from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.ev_charging_stations.pipelines.query_pipeline import run_query_pipeline
from typing import Optional
from fastapi import HTTPException



# -------------------------
# App setup
# -------------------------
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Models
# -------------------------
class QueryModel(BaseModel):
    """Model for incoming query from frontend."""
    query: str
    file_name: str = None  # optional if not needed


class StationOutputModel(BaseModel):
    """Model for each station returned by pipeline."""
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
    avg_sentiment: Optional[float] = None
    num_reviews: Optional[int] = None


class ResponseModel(BaseModel):
    """Model for API response."""
    model_output: list[StationOutputModel]

# -------------------------
# API Endpoints
# -------------------------

@app.post("/process", response_model=ResponseModel)
async def process_query(query_model: QueryModel):
    """Serves the API for the frontend or external calls."""
    stations = run_query_pipeline(query_model.query)
    if stations is None:
        raise HTTPException(status_code=500, detail="Failed to process query. Try again later.(Open Router API KEY error.)")
    return {"model_output": [station.dict() for station in stations]}

@app.get("/")
async def get_index():
    """Serves the HTML UI."""
    html_file = Path(__file__).parent / "index.html"
    return FileResponse(html_file)
