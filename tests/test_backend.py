import os
import sys

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
sys.path.insert(0, BASE_DIR)

def test_all_modules():
    print("Testing KisanShield AI Backend Modules...")

    # 1. Database Init
    from backend.database import init_db, SessionLocal
    init_db()
    print("[OK] Database initialized.")

    # 2. KrishiProof Service
    from backend.services.krishiproof_service import analyze_advice
    adv = analyze_advice("Dealer recommends 3 bags urea for tomato stage 2.")
    assert adv['trust_score'] > 0
    print(f"[OK] KrishiProof Engine tested: Trust Score = {adv['trust_score']}/100")

    # 3. InputTruth Service
    from backend.services.inputtruth_service import analyze_input_bill
    inp = analyze_input_bill(product_name="Urea", purchased_quantity_kg=200, unit_price_rs=12.0, land_area_acres=2.0)
    assert inp['total_spent_rs'] == 2400.0
    print(f"[OK] InputTruth Engine tested: Avoidable cost = Rs. {inp['avoidable_expenditure_rs']}")

    # 4. FarmExit Economics Service
    from backend.services.farmexit_service import calculate_crop_economics
    econ = calculate_crop_economics(money_invested_rs=50000, expected_additional_cost_rs=15000, expected_yield_quintals=60)
    assert 'recommendation' in econ
    print(f"[OK] FarmExit Engine tested: Recommendation = {econ['recommendation']}")

    # 5. MarketShield APMC Net Realization Service
    from backend.services.marketshield_service import analyze_nearby_markets
    mkt = analyze_nearby_markets(farmer_lat=20.0, farmer_lon=73.78, commodity="Onion")
    assert len(mkt['markets']) > 0
    print(f"[OK] MarketShield Engine tested: Best Market = {mkt['best_market']['name']} (Rs. {mkt['best_market']['net_realization_per_q']}/q net)")

    # 6. Price Intelligence Forecast Service
    from backend.services.price_forecast_service import forecast_price_direction
    p_fc = forecast_price_direction(commodity="Onion")
    assert 'direction_label' in p_fc
    print(f"[OK] Price Forecast Engine tested: Direction = {p_fc['direction_code']}")

    # 7. Policy & Trade Intelligence Service
    from backend.services.policy_trade_service import get_policy_and_trade_intelligence
    pol = get_policy_and_trade_intelligence("Onion")
    assert len(pol['policy_events']) > 0
    print(f"[OK] Policy & Trade Engine tested: Found {len(pol['policy_events'])} policies.")

    # 8. What-If Simulator Service
    from backend.services.simulator_service import simulate_market_scenario
    sim = simulate_market_scenario(arrival_change_pct=20.0)
    assert 'simulated_scenario' in sim
    print(f"[OK] What-If Simulator tested: Net price = Rs. {sim['simulated_scenario']['net_price_rs_per_q']}")

    # 9. Unified Master Farm Decision Service
    from backend.services.unified_decision_service import generate_unified_farm_decision
    dec = generate_unified_farm_decision(farmer_name="Ramesh Patil")
    assert 'master_recommendation' in dec
    print(f"[OK] Master Decision Protection Engine tested: Recommendation = {dec['master_recommendation']}")

    print("\nALL BACKEND MODULES VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all_modules()
