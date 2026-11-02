def simulate_market_scenario(
    base_price_rs_per_q: float = 2650.0,
    base_arrivals_tonnes: float = 420.0,
    expected_quantity_q: float = 50.0,
    total_cost_rs: float = 70000.0,
    transport_cost_per_q: float = 180.0,
    arrival_change_pct: float = 20.0, # e.g. +20% arrivals
    price_shock_pct: float = -10.0, # e.g. -10% price fall
    export_restriction: bool = False,
    transport_cost_increase_pct: float = 0.0
):
    # Calculate price impact from arrival elasticity (Typical arrival elasticity ~ -0.35)
    arrival_price_effect_pct = (arrival_change_pct * -0.35)
    
    export_effect_pct = -8.0 if export_restriction else 0.0
    
    total_simulated_price_pct = price_shock_pct + arrival_price_effect_pct + export_effect_pct
    
    simulated_price_rs_per_q = max(500.0, base_price_rs_per_q * (1.0 + (total_simulated_price_pct / 100.0)))
    
    simulated_transport_cost_per_q = transport_cost_per_q * (1.0 + (transport_cost_increase_pct / 100.0))
    
    # Net realization
    current_net_price = max(0.0, base_price_rs_per_q - transport_cost_per_q - 30.0)
    simulated_net_price = max(0.0, simulated_price_rs_per_q - simulated_transport_cost_per_q - 30.0)
    
    current_revenue = expected_quantity_q * current_net_price
    simulated_revenue = expected_quantity_q * simulated_net_price
    
    current_profit = current_revenue - total_cost_rs
    simulated_profit = simulated_revenue - total_cost_rs
    
    profit_delta_rs = simulated_profit - current_profit
    
    if simulated_profit > 20000.0:
        risk_status = "LOW RISK"
        action = "SELL IN BATCHES / HOLD FOR PEAK"
    elif simulated_profit >= 0:
        risk_status = "MODERATE RISK"
        action = "SELL 50% IMMEDIATELY / PROTECT CAPITAL"
    else:
        risk_status = "HIGH FINANCIAL RISK"
        action = "SELL IMMEDIATELY OR EXPORT TO NEARBY MANDI"

    return {
        "disclaimer": "⚠️ SIMULATION — NOT GUARANTEED FUTURE RESULT. Models projected market dynamics.",
        "input_parameters": {
            "arrival_change_pct": arrival_change_pct,
            "price_shock_pct": price_shock_pct,
            "export_restriction": export_restriction,
            "transport_increase_pct": transport_cost_increase_pct
        },
        "current_scenario": {
            "gross_price_rs_per_q": round(base_price_rs_per_q, 2),
            "net_price_rs_per_q": round(current_net_price, 2),
            "total_revenue_rs": round(current_revenue, 2),
            "total_profit_rs": round(current_profit, 2)
        },
        "simulated_scenario": {
            "gross_price_rs_per_q": round(simulated_price_rs_per_q, 2),
            "net_price_rs_per_q": round(simulated_net_price, 2),
            "total_revenue_rs": round(simulated_revenue, 2),
            "total_profit_rs": round(simulated_profit, 2),
            "price_change_pct": round(total_simulated_price_pct, 1),
            "profit_impact_rs": round(profit_delta_rs, 2)
        },
        "simulated_risk_level": risk_status,
        "recommended_mitigation_action": action,
        "impact_breakdown": [
            f"Arrival change of {arrival_change_pct}% alters price by {arrival_price_effect_pct:.1f}%.",
            f"Export restriction applies additional {export_effect_pct:.1f}% market price pressure." if export_restriction else "No export restriction applied.",
            f"Net profit changes by ₹{profit_delta_rs:,.2f} compared to base scenario."
        ]
    }
