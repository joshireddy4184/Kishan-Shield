import datetime
import random
from backend.services.krishiproof_service import analyze_advice
from backend.services.inputtruth_service import analyze_input_bill
from backend.services.farmexit_service import calculate_crop_economics
from backend.services.marketshield_service import analyze_nearby_markets
from backend.services.price_forecast_service import forecast_price_direction
from backend.services.policy_trade_service import get_policy_and_trade_intelligence

def generate_unified_farm_decision(
    farmer_name: str = "Ramesh Patil",
    state: str = "Maharashtra",
    district: str = "Nashik",
    village: str = "Pimpalgaon",
    lat: float = 20.0000,
    lon: float = 73.7800,
    crop: str = "Onion",
    land_area_acres: float = 3.0,
    expected_yield_quintals: float = 50.0,
    money_invested_rs: float = 52000.0,
    expected_additional_cost_rs: float = 18000.0,
    advice_raw_text: str = None,
    input_product_name: str = None,
    input_qty_kg: float = 0.0,
    input_unit_price_rs: float = 0.0
):
    # 1. Advice Trust Engine
    if advice_raw_text:
        advice_res = analyze_advice(advice_raw_text, crop=crop, land_area_acres=land_area_acres)
    else:
        advice_res = analyze_advice(
            "Dealer recommends applying 3 bags of proprietary root booster spray immediately for maximum size.",
            crop=crop, land_area_acres=land_area_acres
        )
        
    # 2. Input Purchase Engine
    if input_product_name and input_qty_kg > 0:
        input_res = analyze_input_bill(
            product_name=input_product_name,
            purchased_quantity_kg=input_qty_kg,
            unit_price_rs=input_unit_price_rs,
            crop=crop, land_area_acres=land_area_acres
        )
    else:
        input_res = analyze_input_bill(
            product_name="Complex NPK Fertilizer & Growth Tonic",
            purchased_quantity_kg=75.0, unit_price_rs=140.0,
            crop=crop, land_area_acres=land_area_acres
        )
        
    # 3. Market Realization Engine
    market_res = analyze_nearby_markets(
        farmer_lat=lat, farmer_lon=lon,
        commodity=crop, quantity_quintals=expected_yield_quintals
    )
    best_market = market_res['best_market']
    
    # 4. ML Price Forecast Engine
    price_res = forecast_price_direction(
        commodity=crop, state=state, market=best_market['name'],
        current_modal_price=best_market['modal_price'],
        current_arrivals_tonnes=best_market['arrivals_tonnes']
    )
    
    # 5. Crop Economics Engine
    econ_res = calculate_crop_economics(
        money_invested_rs=money_invested_rs,
        expected_additional_cost_rs=expected_additional_cost_rs,
        expected_yield_quintals=expected_yield_quintals,
        current_price_rs_per_q=best_market['modal_price'],
        forecast_price_rs_per_q=price_res['upper_bound_rs_per_q'],
        downside_price_rs_per_q=best_market['min_price'],
        transport_cost_per_q=best_market['transport_cost_per_q'],
        storage_cost_per_q=best_market['other_costs_per_q']
    )
    
    # 6. Policy & Trade Engine
    policy_res = get_policy_and_trade_intelligence(commodity=crop)
    
    # 7. UNIFIED DECISION COMPOSER LOGIC
    # Synthesize all 6 engines
    p_dir = price_res['direction_code']
    trust_score = advice_res['trust_score']
    excess_expenditure = input_res['avoidable_expenditure_rs']
    financial_risk = econ_res['financial_risk']
    
    if p_dir == "INCREASE" and financial_risk in ["LOW", "MEDIUM"]:
        action = "SELL PARTIALLY"
        sell_pct = 40.0
        hold_pct = 60.0
        action_color = "emerald"
        primary_reason = f"Current modal price at {best_market['name']} (₹{best_market['net_realization_per_q']:.2f}/q net) is attractive. ML forecast indicates moderate 7-day upside, but policy uncertainty warrants locking in partial revenue (40%) to eliminate financial risk."
    elif p_dir == "INCREASE" and financial_risk == "HIGH":
        action = "SELL NOW"
        sell_pct = 100.0
        hold_pct = 0.0
        action_color = "amber"
        primary_reason = "High financial risk exposure requires immediate liquidity. Sell 100% at optimal nearby APMC."
    elif p_dir == "DECREASE":
        action = "SELL IMMEDIATELY"
        sell_pct = 100.0
        hold_pct = 0.0
        action_color = "rose"
        primary_reason = "Forecast indicates downward price pressure due to increasing regional market arrivals. Liquidate harvest now to prevent margin erosion."
    else:
        action = "SWITCH MARKET / SELL 50%"
        sell_pct = 50.0
        hold_pct = 50.0
        action_color = "blue"
        primary_reason = f"Stable market outlook. Divert transport to {best_market['name']} for best net realization."

    # Compute overall confidence score
    confidence_score = round((price_res['confidence_score_pct'] * 0.5) + (trust_score * 0.3) + 15.0, 1)
    
    # Financial protection metric (avoidable cost + optimal net realization delta)
    second_best_net = market_res['markets'][1]['net_realization_per_q'] if len(market_res['markets']) > 1 else best_market['net_realization_per_q']
    market_selection_gain = (best_market['net_realization_per_q'] - second_best_net) * expected_yield_quintals
    total_financial_protection = round(excess_expenditure + market_selection_gain, 2)
    
    passport_num = f"#{random.randint(100, 999)}"
    
    return {
        "passport_code": f"FARM DECISION {passport_num}",
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "farmer_name": farmer_name,
        "crop": crop,
        "location": f"{village}, {district}, {state}",
        "land_area_acres": land_area_acres,
        "expected_yield_quintals": expected_yield_quintals,
        "master_recommendation": action,
        "sell_ratio_str": f"SELL {sell_pct:.0f}% / HOLD {hold_pct:.0f}%",
        "action_color": action_color,
        "primary_reason": primary_reason,
        "overall_confidence_pct": confidence_score,
        "estimated_financial_protection_rs": total_financial_protection,
        "module_summaries": {
            "krishiproof": {
                "trust_score": f"{trust_score}/100",
                "risk_level": advice_res['risk_level'],
                "bias_risk": advice_res['commercial_bias_risk']
            },
            "inputtruth": {
                "excess_kg": input_res['potential_excess_kg'],
                "avoidable_cost_rs": input_res['avoidable_expenditure_rs'],
                "quantity_risk": input_res['quantity_risk']
            },
            "farmexit": {
                "financial_risk": econ_res['financial_risk'],
                "sunk_cost_rs": econ_res['money_invested_sunk_rs'],
                "break_even_price_rs": econ_res['break_even_price_total_rs'],
                "recommendation": econ_res['recommendation']
            },
            "marketshield": {
                "best_market": best_market['name'],
                "distance_km": best_market['distance_km'],
                "gross_price": best_market['modal_price'],
                "transport_cost": best_market['transport_cost_per_q'],
                "net_realization": best_market['net_realization_per_q']
            },
            "price_forecast": {
                "direction": price_res['direction_label'],
                "expected_range": price_res['forecast_range_str'],
                "confidence": f"{price_res['confidence_score_pct']}%"
            },
            "policy_and_trade": {
                "active_policies": len(policy_res['policy_events']),
                "trade_signal": policy_res['trade_signals'][0]['trade_signal'] if policy_res['trade_signals'] else "STABLE"
            }
        }
    }
