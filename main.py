# nearby_locations_api.py

import os, csv, httpx
from typing import List, Tuple
from geopy.distance import geodesic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATA_PATH = os.path.join("data", "locations.txt")
MAX_DESTINATIONS_PER_CALL = 25

# Initialize FastAPI application
app = FastAPI(title="Nearby Locations API", version="1.0")

# Load locations from a pipe-delimited text file
def load_locations(path: str) -> List[dict]:
    locations = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            if len(row) == 3:
                name, lat, lng = row
                locations.append({"name": name, "lat": float(lat), "lng": float(lng)})
    return locations

# Filter locations within a radius using geodesic distance (in km)
def filter_within_radius(origin: Tuple[float, float], locations: List[dict], radius_km: float) -> List[dict]:
    return [loc for loc in locations if geodesic(origin, (loc["lat"], loc["lng"])).km <= radius_km]

# Use Google Maps Distance Matrix API to get driving distance and duration
async def distance_matrix(origin: Tuple[float, float], destinations: List[str]) -> List[dict]:
    origin_str = f"{origin[0]},{origin[1]}"
    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin_str}&destinations={'|'.join(destinations)}"
        f"&mode=driving&units=metric&key={GOOGLE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
        data = response.json()

    if data.get("status") != "OK":
        raise HTTPException(400, data.get("error_message", "Distance Matrix Error"))

    # Process valid results from the API
    return [
        {
            "destination": dest,
            "distance_km": elem["distance"]["value"] / 1000,
            "duration_min": elem["duration"]["value"] / 60,
        }
        for dest, elem in zip(destinations, data["rows"][0]["elements"])
        if elem["status"] == "OK"
    ]

# Input schema for the POST request
class NearbyRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    radius_km: float
    max_duration_min: float

# API endpoint: get nearby locations by travel time and radius
@app.post("/nearby-locations")
async def nearby_locations(req: NearbyRequest):
    origin = (req.origin_lat, req.origin_lng)
    try:
        locations = load_locations(DATA_PATH)
        candidates = filter_within_radius(origin, locations, req.radius_km)
    except Exception:
        raise HTTPException(500, detail="Error loading or filtering locations")

    if not candidates:
        return []

    destination_coords = [f"{loc['lat']},{loc['lng']}" for loc in candidates]

    # Send queries in batches to comply with API limits
    results = []
    for i in range(0, len(destination_coords), MAX_DESTINATIONS_PER_CALL):
        chunk = destination_coords[i:i + MAX_DESTINATIONS_PER_CALL]
        results.extend(await distance_matrix(origin, chunk))

    # Filter final results by travel time and sort by distance
    filtered = [r for r in results if r["duration_min"] <= req.max_duration_min]
    filtered.sort(key=lambda x: x["distance_km"])
    return filtered

# Run with Uvicorn in development mode
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("nearby_locations_api:app", host="127.0.0.1", port=8000, reload=True)
