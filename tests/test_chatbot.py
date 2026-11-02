import sys
import os

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
sys.path.insert(0, BASE_DIR)

from backend.services.chatbot_decision_service import generate_chatbot_response

def test_chatbot_all_questions():
    print("Testing KisanShield Chatbot Decision Engine across 10 Required Question Types...")

    farmer_context = {
        "name": "Ramesh Patil",
        "crop": "Onion",
        "state": "Maharashtra",
        "district": "Nashik",
        "lat": 20.0000,
        "lon": 73.7800,
        "acres": 3.0,
        "yield_q": 50.0,
        "invested_rs": 52000.0,
        "additional_rs": 18000.0,
        "is_live_location": True
    }

    questions = [
        ("What is my current onion price?", "PRICE_QUERY", "Current Mandi Price Intelligence"),
        ("Should I sell my onion today?", "SELL_WAIT_DECISION", "Recommendation"),
        ("Which mandi should I sell to?", "MANDI_RECOMMENDATION", "Market Ranking by Net Realization"),
        ("What is my investment?", "FARM_ECONOMICS", "Sunk Cost (Money Invested)"),
        ("What happens if onion price falls by 10%?", "WHAT_IF", "Simulated Shock"),
        ("Should I sell everything or wait?", "SELL_WAIT_DECISION", "Recommendation"),
        ("Is this fertilizer recommendation safe?", "INPUT_SAFETY", "Agronomic Input Safety & Trust Evaluation"),
        ("What government policy affects my crop?", "POLICY_TRADE", "Government Policy & Trade Intelligence"),
        ("What did you recommend earlier?", "FARM_MEMORY", "Farm Memory & Previous Decision History"),
        ("Which nearby market gives me the best net realization?", "MANDI_RECOMMENDATION", "Top Recommended APMC Market")
    ]

    for idx, (q, expected_intent, expected_keyword) in enumerate(questions, 1):
        res = generate_chatbot_response(q, farmer_context)
        assert res.get('intent') == expected_intent, f"Q{idx} intent mismatch: expected {expected_intent}, got {res.get('intent')}"
        assert expected_keyword in res['reply'], f"Q{idx} keyword missing: {expected_keyword}"
        print(f"  [OK] Question {idx} ('{q}') -> Intent: {res.get('intent')}")

    print("\nALL 10 CHATBOT QUESTION TYPES TESTED & VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_chatbot_all_questions()
