def calculate_crop_economics(
    money_invested_rs: float = 52000.0,
    expected_additional_cost_rs: float = 18000.0,
    expected_yield_quintals: float = 50.0, # e.g. 5 tonnes = 50 q
    current_price_rs_per_q: float = 2480.0,
    forecast_price_rs_per_q: float = 2600.0,
    downside_price_rs_per_q: float = 1900.0,
    transport_cost_per_q: float = 150.0,
    storage_cost_per_q: float = 30.0
):
    total_cost_rs = money_invested_rs + expected_additional_cost_rs
    total_logistics_per_q = transport_cost_per_q + storage_cost_per_q
    
    # Net price realized after logistics
    expected_net_price = max(0.0, forecast_price_rs_per_q - total_logistics_per_q)
    downside_net_price = max(0.0, downside_price_rs_per_q - total_logistics_per_q)
    
    # Financial metrics
    expected_revenue = expected_yield_quintals * expected_net_price
    downside_revenue = expected_yield_quintals * downside_net_price
    
    expected_profit = expected_revenue - total_cost_rs
    downside_profit = downside_revenue - total_cost_rs
    
    # Break-even calculations
    # 1. Total Cost Break-Even Price
    be_price_total = (total_cost_rs / (expected_yield_quintals + 1e-5)) + total_logistics_per_q
    # 2. Sunk-Cost-Adjusted (Remaining Investment Only) Break-Even Price
    be_price_remaining = (expected_additional_cost_rs / (expected_yield_quintals + 1e-5)) + total_logistics_per_q
    
    # Break-Even Yield (quintals)
    be_yield_total = total_cost_rs / (expected_net_price + 1e-5)
    
    # Recovery probability & decision rule
    roi_pct = (expected_profit / (total_cost_rs + 1e-5)) * 100
    
    if expected_net_price >= be_price_total and roi_pct > 15.0:
        recommendation = "CONTINUE"
        financial_risk = "LOW"
        reason = "Expected price comfortable covers total crop investment with positive ROI."
    elif expected_net_price >= be_price_remaining:
        recommendation = "REDUCE INVESTMENT"
        financial_risk = "MEDIUM"
        reason = "Expected price covers remaining marginal cost but total profit margin is slim. Minimize additional expenditure."
    else:
        recommendation = "CONSIDER EXIT / SWITCH CROP"
        financial_risk = "HIGH"
        reason = "Forecast price fails to cover even remaining investment costs. Further capital input risks expanding losses."

    return {
        "money_invested_sunk_rs": round(money_invested_rs, 2),
        "expected_additional_cost_rs": round(expected_additional_cost_rs, 2),
        "total_cost_rs": round(total_cost_rs, 2),
        "expected_yield_quintals": round(expected_yield_quintals, 1),
        "current_price_rs_per_q": round(current_price_rs_per_q, 2),
        "forecast_price_rs_per_q": round(forecast_price_rs_per_q, 2),
        "expected_net_price_rs_per_q": round(expected_net_price, 2),
        "expected_revenue_rs": round(expected_revenue, 2),
        "expected_profit_rs": round(expected_profit, 2),
        "downside_scenario_profit_rs": round(downside_profit, 2),
        "break_even_price_total_rs": round(be_price_total, 2),
        "break_even_price_remaining_rs": round(be_price_remaining, 2),
        "break_even_yield_quintals": round(be_yield_total, 1),
        "roi_percentage": round(roi_pct, 2),
        "financial_risk": financial_risk,
        "recommendation": recommendation,
        "recommendation_reason": reason,
        "assumptions": [
            f"Expected harvest yield: {expected_yield_quintals} quintals.",
            f"Transport and handling costs estimated at ₹{total_logistics_per_q:.2f}/quintal.",
            f"Sunk cost of ₹{money_invested_rs:,.2f} already incurred; decision evaluated on marginal return of remaining ₹{expected_additional_cost_rs:,.2f}."
        ]
    }
