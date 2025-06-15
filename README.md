# Nearby Locations API

This FastAPI-based project allows you to find nearby cities or towns from a given origin point, filtering by radius and maximum travel time using Google Distance Matrix API.

## Features

- Load predefined location coordinates from a text file.
- Filter nearby locations by geodesic distance.
- Send batches of destinations to Google Distance Matrix API.
- Filter by maximum driving duration in minutes.

## Requirements

- Python 3.9+
- Packages listed in `requirements.txt`
- Google Distance Matrix API key

## File Structure

```
📁 data/
    └── locations.txt         # List of locations (name|lat|lng), one per line.
📄 nearby_locations_api.py    # Main API script.
📄 fetch_locations.py         # Script to generate location data from OpenStreetMap.
📄 requirements.txt           # Python dependencies.
📄 .env.example               # Template for environment variables.
```

## Setup

1. Clone the repository and navigate into it.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example` and add your Google Maps API key.
5. Run the API:
   ```bash
   uvicorn nearby_locations_api:app --reload
   ```

## Endpoint

### `POST /nearby-locations`

**Body:**
```json
{
  "origin_lat": 41.3851,
  "origin_lng": 2.1734,
  "radius_km": 50,
  "max_duration_min": 60
}
```

**Response:**
```json
[
  {
    "destination": "41.0,1.5",
    "distance_km": 35.2,
    "duration_min": 42.3
  }
]
```

## Notes

- The API sends requests in chunks of 25 destinations due to Google API limitations.
- Use `fetch_locations.py` to dynamically generate location datasets from OpenStreetMap.

---

MIT License