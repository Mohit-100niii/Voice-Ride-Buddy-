import httpx
from math import radians, sin, cos, sqrt, atan2

# Function to calculate distance between two lat/lon using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return round(distance, 2)  # in kilometers

async def get_distance_from_osm(pickup: str, drop: str):
    async with httpx.AsyncClient() as client:
        pickup_resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": pickup, "format": "json", "limit": 1},
            headers={"User-Agent": "ridebuddy-app"}
        )
        drop_resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": drop, "format": "json", "limit": 1},
            headers={"User-Agent": "ridebuddy-app"}
        )

        pickup_data = pickup_resp.json()
        drop_data = drop_resp.json()

        if not pickup_data or not drop_data:
            return {"error": "Could not geocode one of the addresses"}

        # Extract coordinates as floats
        lat1, lon1 = float(pickup_data[0]["lat"]), float(pickup_data[0]["lon"])
        lat2, lon2 = float(drop_data[0]["lat"]), float(drop_data[0]["lon"])

        # Calculate distance
        distance_km = haversine(lat1, lon1, lat2, lon2)

        return {
            "distance_km": distance_km
        }
