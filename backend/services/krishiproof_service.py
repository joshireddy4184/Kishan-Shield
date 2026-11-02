import re

def analyze_advice(raw_text: str, crop: str = "Onion", land_area_acres: float = 3.0):
    raw_lower = raw_text.lower()
    
    # Extract entities using pattern rules
    extracted_crop = crop
    if "tomato" in raw_lower:
        extracted_crop = "Tomato"
    elif "onion" in raw_lower:
        extracted_crop = "Onion"
    elif "potato" in raw_lower:
        extracted_crop = "Potato"
    elif "wheat" in raw_lower:
        extracted_crop = "Wheat"
        
    extracted_input = "Chemical Booster / Foliar Spray"
    if "urea" in raw_lower:
        extracted_input = "Urea Fertilizer"
    elif "dap" in raw_lower:
        extracted_input = "DAP (Di-ammonium Phosphate)"
    elif "pesticide" in raw_lower or "spray" in raw_lower:
        extracted_input = "Synthetic Pesticide / Fungicide"
    elif "growth promoter" in raw_lower or "tonic" in raw_lower:
        extracted_input = "Bio-growth Tonic / Special Micronutrient"

    # Evaluate factors
    missing_info = []
    if not any(k in raw_lower for k in ["stage", "week", "days after", "vegetative", "flowering"]):
        missing_info.append("Missing crop growth stage specification")
    if not any(k in raw_lower for k in ["severity", "spot", "blight", "infestation", "per acre"]):
        missing_info.append("Missing pest/disease severity criteria or exact dosage per acre")
    if not any(k in raw_lower for k in ["soil test", "water", "irrigation"]):
        missing_info.append("No consideration for soil moisture or existing soil nutrients")

    # Commercial bias scoring
    commercial_bias_risk = "LOW"
    if any(k in raw_lower for k in ["must buy", "dealer recommendation", "brand", "double yield", "guaranteed 100%"]):
        commercial_bias_risk = "HIGH"
    elif any(k in raw_lower for k in ["promoter", "tonic", "dealer", "shop"]):
        commercial_bias_risk = "MEDIUM"

    # Source reliability
    source_reliability = "MODERATE"
    if "official" in raw_lower or "kvk" in raw_lower or "university" in raw_lower or "icar" in raw_lower:
        source_reliability = "HIGH (Institutional)"
    elif "whatsapp" in raw_lower or "dealer" in raw_lower or "youtube" in raw_lower:
        source_reliability = "UNVERIFIED (Social/Dealer Channel)"

    # Evidence strength
    evidence_strength = "WEAK"
    if len(missing_info) == 0:
        evidence_strength = "STRONG"
    elif len(missing_info) == 1:
        evidence_strength = "MODERATE"

    # Compute Trust Score out of 100
    base_score = 85
    if commercial_bias_risk == "HIGH":
        base_score -= 20
    elif commercial_bias_risk == "MEDIUM":
        base_score -= 10
        
    if source_reliability.startswith("UNVERIFIED"):
        base_score -= 15
        
    base_score -= (len(missing_info) * 10)
    trust_score = max(20, min(95, base_score))

    risk_level = "LOW"
    if trust_score < 60:
        risk_level = "HIGH"
    elif trust_score < 75:
        risk_level = "MEDIUM"

    reasons = []
    if missing_info:
        reasons.append(f"The recommendation lacks specific details: {', '.join(missing_info).lower()}.")
    if commercial_bias_risk in ["MEDIUM", "HIGH"]:
        reasons.append("Potential commercial bias detected favoring specific proprietary inputs or high dosages.")
    if source_reliability.startswith("UNVERIFIED"):
        reasons.append("Advice originates from an unverified social or retail sales channel without university/KVK peer review.")

    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "extracted_crop": extracted_crop,
        "extracted_input": extracted_input,
        "evidence_strength": evidence_strength,
        "source_reliability": source_reliability,
        "farmer_applicability": "PARTIAL — Requires stage verification before application",
        "commercial_bias_risk": commercial_bias_risk,
        "missing_information": missing_info,
        "reasons": reasons,
        "recommendation": "DO NOT BUY IMMEDIATELY. Verify crop stage and consult local KVK or agricultural officer." if trust_score < 65 else "PROCEED WITH CAUTION. Apply recommended dosage only."
    }
