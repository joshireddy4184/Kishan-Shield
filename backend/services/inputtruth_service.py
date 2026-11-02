import os
import pandas as pd

# Standard benchmark agronomic input limits per acre for common crops (in kg/acre)
AGRONOMIC_BENCHMARKS = {
    "Onion": {"Urea": 45.0, "DAP": 30.0, "MOP": 25.0, "Pesticide": 2.5, "Micronutrients": 5.0},
    "Tomato": {"Urea": 50.0, "DAP": 40.0, "MOP": 30.0, "Pesticide": 3.0, "Micronutrients": 6.0},
    "Potato": {"Urea": 60.0, "DAP": 50.0, "MOP": 40.0, "Pesticide": 3.5, "Micronutrients": 7.0},
    "Wheat": {"Urea": 55.0, "DAP": 35.0, "MOP": 20.0, "Pesticide": 1.5, "Micronutrients": 4.0},
    "Rice": {"Urea": 50.0, "DAP": 30.0, "MOP": 20.0, "Pesticide": 2.0, "Micronutrients": 5.0}
}

def analyze_input_bill(
    product_name: str = "Special Soil Booster & Complex Fertilizer",
    input_type: str = "Fertilizer",
    purchased_quantity_kg: float = 75.0,
    unit_price_rs: float = 140.0,
    crop: str = "Onion",
    land_area_acres: float = 3.0,
    crop_stage: str = "Vegetative"
):
    total_spent = purchased_quantity_kg * unit_price_rs
    
    crop_benchmarks = AGRONOMIC_BENCHMARKS.get(crop, AGRONOMIC_BENCHMARKS["Onion"])
    
    # Map input category to benchmark key
    bench_key = "Urea"
    p_lower = product_name.lower()
    if "pesticide" in p_lower or "fungicide" in p_lower or "insecticide" in p_lower:
        bench_key = "Pesticide"
    elif "dap" in p_lower:
        bench_key = "DAP"
    elif "booster" in p_lower or "tonic" in p_lower or "micronutrient" in p_lower:
        bench_key = "Micronutrients"
        
    recommended_per_acre = crop_benchmarks.get(bench_key, 35.0)
    
    # Total recommended for farmer's land area
    total_recommended_kg = recommended_per_acre * land_area_acres
    
    potential_excess_kg = max(0.0, purchased_quantity_kg - total_recommended_kg)
    avoidable_expenditure_rs = potential_excess_kg * unit_price_rs
    
    excess_pct = (potential_excess_kg / (total_recommended_kg + 1e-5)) * 100
    
    quantity_risk = "LOW"
    if excess_pct > 50.0:
        quantity_risk = "HIGH"
    elif excess_pct > 15.0:
        quantity_risk = "MEDIUM"

    assessment_language = "Potentially excessive based on available agronomic benchmark information." if potential_excess_kg > 0 else "Purchase aligns with recommended agronomic guidelines."

    return {
        "product_name": product_name,
        "input_type": input_type,
        "crop": crop,
        "land_area_acres": land_area_acres,
        "purchased_quantity_kg": purchased_quantity_kg,
        "unit_price_rs": unit_price_rs,
        "total_spent_rs": round(total_spent, 2),
        "recommended_quantity_kg": round(total_recommended_kg, 1),
        "potential_excess_kg": round(potential_excess_kg, 1),
        "avoidable_expenditure_rs": round(avoidable_expenditure_rs, 2),
        "quantity_risk": quantity_risk,
        "assessment_note": assessment_language,
        "reasons": [
            f"For {land_area_acres} acres of {crop} at {crop_stage} stage, standard agronomic requirement is ~{total_recommended_kg:.1f} kg.",
            f"Purchased quantity ({purchased_quantity_kg} kg) exceeds benchmark by {potential_excess_kg:.1f} kg ({excess_pct:.1f}%).",
            f"Potential avoidable expenditure: ₹{avoidable_expenditure_rs:,.2f}."
        ] if potential_excess_kg > 0 else ["Purchased quantity matches state agronomic recommendations."]
    }
