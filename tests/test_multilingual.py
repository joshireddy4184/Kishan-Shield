import sys
import os

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
sys.path.insert(0, BASE_DIR)

from backend.services.chatbot_decision_service import generate_chatbot_response

def test_multilingual_chatbot():
    print("Testing KisanShield Multilingual Chatbot Responses (en, hi, te, ta)...")

    farmer_context = {
        "name": "Ramesh Patil",
        "crop": "Onion",
        "state": "Maharashtra",
        "district": "Nashik",
        "lat": 20.0000,
        "lon": 73.7800,
        "acres": 3.0,
        "yield_q": 50.0,
        "is_live_location": True
    }

    # Test 1: English
    farmer_context["language"] = "en"
    res_en = generate_chatbot_response("Should I sell my onion today?", farmer_context)
    assert "**Recommendation**" in res_en['reply']
    print("  [OK] English Response Verified.")

    # Test 2: Hindi
    farmer_context["language"] = "hi"
    res_hi = generate_chatbot_response("क्या मुझे आज अपना प्याज बेचना चाहिए?", farmer_context)
    assert len(res_hi['reply']) > 50
    print("  [OK] Hindi Response Verified.")

    # Test 3: Telugu
    farmer_context["language"] = "te"
    res_te = generate_chatbot_response("నేను ఈరోజు ఉల్లిపాయలను అమ్మాలా?", farmer_context)
    assert len(res_te['reply']) > 50
    print("  [OK] Telugu Response Verified.")

    # Test 4: Tamil
    farmer_context["language"] = "ta"
    res_ta = generate_chatbot_response("இன்று வெங்காயத்தை விற்கலாமா?", farmer_context)
    assert len(res_ta['reply']) > 50
    print("  [OK] Tamil Response Verified.")

    print("\nALL 4 LANGUAGES (EN, HI, TE, TA) VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_multilingual_chatbot()
