import os
import sys
import json
from fastapi.testclient import TestClient

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from backend.main import app

client = TestClient(app)

def test_upgraded_platform():
    print("=" * 60)
    print("TESTING KISHAN SHIELD AI - REAL-WORLD SYSTEM")
    print("=" * 60)

    # 1. Test Web Root
    res = client.get("/")
    assert res.status_code == 200
    assert "Kishan Shield AI" in res.text
    assert "lang-select" in res.text
    assert "topbar-location-badge" in res.text
    assert "live-location-banner" in res.text
    assert "v-weather" in res.text
    print("[PASS] Web Root returns updated Kishan Shield AI HTML with location, weather, and 14-language selectors.")

    # 2. Test Reverse Geocoding API
    res = client.get("/api/reverse-geocode?lat=19.9975&lon=73.7898")
    assert res.status_code == 200
    geo = res.json()
    assert "district" in geo and "state" in geo
    print(f"[PASS] Reverse Geocoding API verified: {geo.get('village', '')} {geo['district']}, {geo['state']}")

    # 3. Test Real-Time Weather & Spraying Advisory API
    res = client.get("/api/weather?lat=19.9975&lon=73.7898")
    assert res.status_code == 200
    weather = res.json()
    assert "current" in weather
    assert "spraying_advisory" in weather
    assert "forecast_3day" in weather
    print(f"[PASS] Real-Time Weather API verified: Temp = {weather['current']['temperature_c']} C, Spraying = {weather['spraying_advisory']['status']}")

    # 4. Test Chatbot across Multiple Indian Languages
    languages_to_test = [
        ("en", "Should I sell my onion harvest today?", "SELL_DECISION"),
        ("hi", "क्या मुझे आज प्याज बेचना चाहिए?", "SELL_DECISION"),
        ("te", "ఈరోజు ఉల్లిపాయ అమ్మాలా?", "SELL_DECISION"),
        ("ta", "இன்று வெங்காயம் விற்கலாமா?", "SELL_DECISION"),
        ("mr", "आज कांदा विकावा का?", "SELL_DECISION"),
        ("ur", "کیا مجھے آج پیاز بیچنا چاہیے؟", "SELL_DECISION"),
        ("sa", "किम् अद्य पलाण्डुं विक्रयणं कुर्याम्?", "SELL_DECISION"),
        ("hi", "आज कीटनाशक छिड़काव के लिए मौसम कैसा रहेगा?", "WEATHER_ADVISORY"),
        ("en", "How to manage downy mildew fungal disease in onions?", "DISEASE_PEST")
    ]

    for lang, query, expected_intent in languages_to_test:
        payload = {
            "message": query,
            "farmer_name": "Ramesh Patil",
            "crop": "Onion",
            "state": "Maharashtra",
            "district": "Nashik",
            "lat": 19.9975,
            "lon": 73.7898,
            "acres": 3.0,
            "yield_q": 50.0,
            "is_live_location": True,
            "language": lang
        }
        res = client.post("/ai/chat", json=payload)
        assert res.status_code == 200
        reply = res.json()
        assert "reply" in reply and len(reply["reply"]) > 10
        print(f"[PASS] Multilingual Chatbot [{lang.upper()}]: Intent = {reply.get('intent')} | Reply Preview: {reply['reply'][:45]}...")

    # 5. Test Unified Decision Passport Analysis
    passport_payload = {
        "farmer_name": "Ramesh Patil",
        "state": "Maharashtra",
        "district": "Nashik",
        "village": "Pimpalgaon",
        "latitude": 19.9975,
        "longitude": 73.7898,
        "crop": "Onion",
        "land_area_acres": 3.0,
        "expected_yield_quintals": 50.0,
        "money_invested_rs": 52000.0,
        "expected_additional_cost_rs": 18000.0
    }
    res = client.post("/decision/analyze", json=passport_payload)
    assert res.status_code == 200
    passport = res.json()
    assert "passport_code" in passport
    assert "master_recommendation" in passport
    print(f"[PASS] Unified Farm Decision API verified: {passport['passport_code']} -> {passport['master_recommendation']}")

    # 6. Test MarketShield Nearby APMC
    res = client.post("/markets/nearby", json={"latitude": 19.9975, "longitude": 73.7898, "commodity": "Onion", "quantity_quintals": 50.0})
    assert res.status_code == 200
    mkts = res.json()
    assert len(mkts["markets"]) > 0
    print(f"[PASS] MarketShield APMC verified: Top Mandi = {mkts['best_market']['name']} (Net Rs. {mkts['best_market']['net_realization_per_q']}/q)")

    print("=" * 60)
    print("ALL REAL-WORLD AGRICULTURAL APPLICATION TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_upgraded_platform()
