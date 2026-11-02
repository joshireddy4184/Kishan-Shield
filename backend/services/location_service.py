import urllib.request
import urllib.parse
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Known representative coordinates of Indian states & major districts for resilient fallback
INDIAN_DISTRICT_FALLBACKS = [
    {"state": "Maharashtra", "district": "Nashik", "lat": 19.9975, "lon": 73.7898},
    {"state": "Maharashtra", "district": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"state": "Maharashtra", "district": "Nagpur", "lat": 21.1458, "lon": 79.0882},
    {"state": "Telangana", "district": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"state": "Telangana", "district": "Warangal", "lat": 17.9689, "lon": 79.5941},
    {"state": "Andhra Pradesh", "district": "Guntur", "lat": 16.3067, "lon": 80.4365},
    {"state": "Andhra Pradesh", "district": "Kurnool", "lat": 15.8281, "lon": 78.0373},
    {"state": "Tamil Nadu", "district": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    {"state": "Tamil Nadu", "district": "Madurai", "lat": 9.9252, "lon": 78.1198},
    {"state": "Karnataka", "district": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    {"state": "Karnataka", "district": "Belagavi", "lat": 15.8497, "lon": 74.4977},
    {"state": "Kerala", "district": "Palakkad", "lat": 10.7867, "lon": 76.6548},
    {"state": "Punjab", "district": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
    {"state": "Haryana", "district": "Karnal", "lat": 29.6857, "lon": 76.9905},
    {"state": "Uttar Pradesh", "district": "Varanasi", "lat": 25.3176, "lon": 82.9739},
    {"state": "Madhya Pradesh", "district": "Indore", "lat": 22.7196, "lon": 75.8577},
    {"state": "Gujarat", "district": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    {"state": "West Bengal", "district": "Bardhaman", "lat": 23.2324, "lon": 87.8615},
    {"state": "Bihar", "district": "Patna", "lat": 25.5941, "lon": 85.1376},
    {"state": "Rajasthan", "district": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    {"state": "Odisha", "district": "Cuttack", "lat": 20.4625, "lon": 85.8828},
    {"state": "Assam", "district": "Kamrup", "lat": 26.1445, "lon": 91.7362}
]

def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Converts GPS coordinates into real-world Indian locality, district, state, and country.
    Uses OpenStreetMap Nominatim with strict timeout, and falls back to proximity calculation
    if internet is restricted or external service is rate-limited.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "KishanShieldAI/2.0 (Agricultural Decision Platform; contact@kishanshield.org)",
                "Accept-Language": "en"
            }
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                address = data.get("address", {})
                
                village = (
                    address.get("village") or
                    address.get("suburb") or
                    address.get("town") or
                    address.get("neighbourhood") or
                    address.get("hamlet") or
                    address.get("city") or
                    "Locality"
                )
                district = (
                    address.get("state_district") or
                    address.get("district") or
                    address.get("county") or
                    address.get("city") or
                    "District"
                )
                state = address.get("state") or "State"
                country = address.get("country") or "India"
                display_name = data.get("display_name", f"{village}, {district}, {state}")
                
                return {
                    "status": "success",
                    "source": "REAL_TIME_GEOLOCATION",
                    "latitude": round(lat, 5),
                    "longitude": round(lon, 5),
                    "village": village,
                    "district": district,
                    "state": state,
                    "country": country,
                    "display_name": display_name,
                    "formatted_location": f"{village}, {district}, {state}"
                }
    except Exception as e:
        logger.warning(f"Nominatim reverse geocode lookup failed ({e}), using proximity estimation.")
    
    # Proximity estimation fallback for Indian coordinates
    best_match = None
    min_dist_sq = float("inf")
    for d in INDIAN_DISTRICT_FALLBACKS:
        dist_sq = (d["lat"] - lat) ** 2 + (d["lon"] - lon) ** 2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_match = d
            
    if best_match and min_dist_sq < 25.0:  # within ~500km
        return {
            "status": "success",
            "source": "PROXIMITY_GPS_ESTIMATE",
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "village": "Local Farm Area",
            "district": best_match["district"],
            "state": best_match["state"],
            "country": "India",
            "display_name": f"Near {best_match['district']}, {best_match['state']}, India",
            "formatted_location": f"Near {best_match['district']}, {best_match['state']}"
        }

    return {
        "status": "partial",
        "source": "RAW_COORDINATES",
        "latitude": round(lat, 5),
        "longitude": round(lon, 5),
        "village": "Rural Locality",
        "district": "Local Agricultural Region",
        "state": "India",
        "country": "India",
        "display_name": f"Coordinates: {lat:.4f}° N, {lon:.4f}° E",
        "formatted_location": f"Coordinates ({lat:.4f}, {lon:.4f})"
    }
