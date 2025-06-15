import requests
import csv
import os

# Change this to any region you want (e.g., "Cataluña", "Lombardia", "Île-de-France")
REGION_NAME = "Lombardia"

# Overpass API setup
overpass_url = "https://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json][timeout:50];
area["name"="{REGION_NAME}"]["admin_level"="4"]->.region;
(
  node["place"~"city|town|village|hamlet"](area.region);
);
out body;
"""

# Make request
print(f"Fetching locations for region: {REGION_NAME}")
response = requests.post(overpass_url, data={"data": overpass_query})
data = response.json()

# Process results
results = []
for element in data["elements"]:
    name = element["tags"].get("name")
    lat = element.get("lat")
    lon = element.get("lon")
    if name and lat and lon:
        results.append((name, lat, lon))

# Save to data/locations.txt
os.makedirs("data", exist_ok=True)
with open("data/locations.txt", "w", newline="", encoding="utf-8") as txtfile:
    writer = csv.writer(txtfile, delimiter="|")
    for row in results:
        writer.writerow(row)

print(f"Saved {len(results)} locations to 'data/locations.txt'")
