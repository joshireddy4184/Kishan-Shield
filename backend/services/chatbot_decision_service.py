import datetime
from typing import Dict, Any, Optional

from backend.services.marketshield_service import analyze_nearby_markets
from backend.services.price_forecast_service import forecast_price_direction
from backend.services.krishiproof_service import analyze_advice
from backend.services.inputtruth_service import analyze_input_bill
from backend.services.farmexit_service import calculate_crop_economics
from backend.services.policy_trade_service import get_policy_and_trade_intelligence
from backend.services.simulator_service import simulate_market_scenario
from backend.services.unified_decision_service import generate_unified_farm_decision
from backend.services.weather_service import get_realtime_weather

# Language detection across all 14 Indian languages
def detect_language(query: str, requested_lang: str = "en") -> str:
    q = query.lower()
    
    # Check for specific script unicode ranges
    if any('\u0c00' <= char <= '\u0c7f' for char in query) or any(k in q for k in ["ఎంత", "ధర", "అమ్మాలా", "ఉల్లిపాయ", "మార్కెట్", "లాభం"]):
        return "te"
    elif any('\u0b80' <= char <= '\u0bff' for char in query) or any(k in q for k in ["விற்க", "விலை", "வெங்காயம்", "சந்தை"]):
        return "ta"
    elif any('\u0c80' <= char <= '\u0cff' for char in query) or any(k in q for k in ["ಬೆಲೆ", "ಮಾರಾಟ", "ಮಾರುಕಟ್ಟೆ", "ಗೊಬ್ಬರ"]):
        return "kn"
    elif any('\u0d00' <= char <= '\u0d7f' for char in query) or any(k in q for k in ["വില", "വിപണി", "കൃഷി", "ലാഭം"]):
        return "ml"
    elif any('\u0a80' <= char <= '\u0aff' for char in query) or any(k in q for k in ["ભાવ", "વેચવું", "ખાતર", "યાર્ડ"]):
        return "gu"
    elif any('\u0a00' <= char <= '\u0a7f' for char in query) or any(k in q for k in ["ਭਾਅ", "ਵੇਚਣਾ", "ਮੰਡੀ", "ਖਾਦ"]):
        return "pa"
    elif any('\u0b00' <= char <= '\u0b7f' for char in query) or any(k in q for k in ["ଦର", "ବିକ୍ରି", "ମଣ୍ଡି", "ଖତ"]):
        return "or"
    elif any('\u0600' <= char <= '\u06ff' for char in query) or any(k in q for k in ["قیمت", "فروخت", "منڈی", "کھاد"]):
        return "ur"
    elif any('\u0980' <= char <= '\u09ff' for char in query):
        if requested_lang == "as" or any(k in q for k in ["দৰ", "বজাৰ", "শস্য"]):
            return "as"
        return "bn"
    elif any('\u0900' <= char <= '\u097f' for char in query):
        if requested_lang == "mr" or any(k in q for k in ["विकू", "भाव", "बाजार", "कांदा", "नफा"]):
            return "mr"
        elif requested_lang == "sa" or any(k in q for k in ["मूल्यम्", "विक्रयणम्", "विपणिः", "सस्यम्"]):
            return "sa"
        return "hi"
    elif requested_lang in ["hi", "te", "ta", "mr", "kn", "bn", "gu", "ml", "pa", "or", "as", "ur", "sa", "en"]:
        return requested_lang
        
    return "en"

# Multilingual labels and footers dictionary
FOOTER_LABELS = {
    "en": {"loc_live": "📍 Live Device GPS Location", "loc_manual": "⚙️ Location: ", "time": "Data Last Updated"},
    "hi": {"loc_live": "📍 लाइव जीपीएस स्थान", "loc_manual": "⚙️ स्थान: ", "time": "अंतिम अद्यतन"},
    "te": {"loc_live": "📍 లైవ్ GPS స్థానం", "loc_manual": "⚙️ స్థానం: ", "time": "చివరి నవీకరణ"},
    "ta": {"loc_live": "📍 நேரலை GPS இருப்பிடம்", "loc_manual": "⚙️ இருப்பிடம்: ", "time": "கடைசியாக புதுப்பிக்கப்பட்டது"},
    "mr": {"loc_live": "📍 थेट GPS स्थान", "loc_manual": "⚙️ स्थान: ", "time": "शेवटचे अपडेट"},
    "kn": {"loc_live": "📍 ಲೈವ್ GPS ಸ್ಥಳ", "loc_manual": "⚙️ ಸ್ಥಳ: ", "time": "ಕೊನೆಯ ಅಪ್ಡೇಟ್"},
    "bn": {"loc_live": "📍 লাইভ GPS অবস্থান", "loc_manual": "⚙️ অবস্থান: ", "time": "সর্বশেষ আপডেট"},
    "gu": {"loc_live": "📍 લાઇવ GPS સ્થાન", "loc_manual": "⚙️ સ્થાન: ", "time": "છેલ્લું અપડેટ"},
    "ml": {"loc_live": "📍 ലൈവ് GPS ലൊക്കേഷൻ", "loc_manual": "⚙️ ലൊക്കേഷൻ: ", "time": "അവസാന അപ്ഡേറ്റ്"},
    "pa": {"loc_live": "📍 ਲਾਈਵ GPS ਸਥਾਨ", "loc_manual": "⚙️ ਸਥਾਨ: ", "time": "ਆਖਰੀ ਅਪਡੇਟ"},
    "or": {"loc_live": "📍 ଲାଇଭ୍ GPS ସ୍ଥାନ", "loc_manual": "⚙️ ସ୍ଥାନ: ", "time": "ଶେଷ ଅପଡେଟ୍"},
    "as": {"loc_live": "📍 লাইভ GPS অৱস্থান", "loc_manual": "⚙️ অৱস্থান: ", "time": "শেহতীয়া আপডেট"},
    "ur": {"loc_live": "📍 لائیو GPS مقام", "loc_manual": "⚙️ مقام: ", "time": "آخری اپ ڈیٹ"},
    "sa": {"loc_live": "📍 प्रत्यक्षం GPS स्थानम्", "loc_manual": "⚙️ स्थानम्: ", "time": "अद्यतनकालः"}
}

def generate_chatbot_response(
    query: str,
    farmer_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if not farmer_context:
        farmer_context = {}
        
    farmer_name = farmer_context.get("name", "Farmer")
    crop = farmer_context.get("crop", "Onion")
    state = farmer_context.get("state", "Maharashtra")
    district = farmer_context.get("district", "Nashik")
    village = farmer_context.get("village", "Local Farm")
    lat = farmer_context.get("lat") or 19.9975
    lon = farmer_context.get("lon") or 73.7898
    acres = farmer_context.get("acres", 3.0)
    yield_q = farmer_context.get("yield_q", 50.0)
    invested_rs = farmer_context.get("invested_rs", 52000.0)
    additional_rs = farmer_context.get("additional_rs", 18000.0)
    is_live_loc = farmer_context.get("is_live_location", False)
    req_lang = farmer_context.get("language", "en")
    
    lang = detect_language(query, req_lang)
    now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    
    # Location string for footer
    f_lbl = FOOTER_LABELS.get(lang, FOOTER_LABELS["en"])
    if is_live_loc:
        loc_str = f"{f_lbl['loc_live']} ({lat:.4f}, {lon:.4f}) 🟢"
    else:
        loc_str = f"{f_lbl['loc_manual']} {district}, {state} 🟡"
        
    footer = f"\n\n---\nℹ️ {loc_str}\n🕒 {f_lbl['time']}: {now_str}"
    q_lower = query.lower().strip()

    # 1. WEATHER & SPRAYING ADVISORY
    if any(k in q_lower for k in ["weather", "rain", "temperature", "spray", "spraying", "humidity", "मौसम", "बारिश", "छिड़काव", "వాతావరణం", "వర్షం", "வானிலை", "மழை", "हवामान", "पाऊस", "ಹವಾಮಾನ", "മഴ", "বৃষ্টি", "વરસાદ", "ਮੀਂਹ", "ବର୍ଷା", "বতৰ", "موسم", "بارش"]):
        weather = get_realtime_weather(lat, lon)
        temp = weather.get("temperature_c", 28.0)
        hum = weather.get("humidity_percent", 65.0)
        rain = weather.get("precipitation_mm", 0.0)
        wind = weather.get("wind_speed_kmh", 12.0)
        cond = weather.get("condition", "Partly Cloudy")
        icon = weather.get("icon", "🌤️")
        spray_suit = weather.get("spray_suitability", "Check field conditions before foliar spraying.")
        
        if lang == "hi":
            reply = f"""**वास्तविक मौसम एवं छिड़काव परामर्श ({district})** {icon}

• **वर्तमान तापमान**: {temp}°C | **मौसम**: {cond}
• **हवा में नमी (Humidity)**: {hum}%
• **बारिश की संभावना**: {rain} मिमी | **हवा की गति**: {wind} किमी/घंटा

**कृषि छिड़काव परामर्श:**
👉 **{spray_suit}**
{"⚠️ भारी हवा या बारिश में कीटनाशक का छिड़काव न करें ताकि दवा का बहाव न हो।" if wind > 18 or rain > 1.0 else "✅ वर्तमान मौसम खाद और कीटनाशक छिड़काव के लिए अनुकूल है।"}{footer}"""
        elif lang == "te":
            reply = f"""**నిజ-సమయ వాతావరణం & స్ప్రే సలహా ({district})** {icon}

• **ప్రస్తుత ఉష్ణోగ్రత**: {temp}°C | **పరిస్థితి**: {cond}
• **తేమ శాతం**: {hum}%
• **వర్షపాతం**: {rain} మిమీ | **గాలి వేగం**: {wind} కిమీ/గం

**మందుల పిచికారీ సలహా:**
👉 **{spray_suit}**
{"⚠️ వర్షం లేదా అధిక గాలి ఉన్నప్పుడు రసాయన మందులను పిచికారీ చేయవద్దు." if wind > 18 or rain > 1.0 else "✅ ప్రస్తుత వాతావరణం ఎరువులు మరియు మందుల పిచికారీకి అనుకూలంగా ఉంది."}{footer}"""
        elif lang == "ta":
            reply = f"""**நேரலை வானிலை & தெளிப்பு ஆலோசனை ({district})** {icon}

• **வெப்பநிலை**: {temp}°C | **வானிலை**: {cond}
• **ஈரப்பதம்**: {hum}% | **காற்று வேகம்**: {wind} கி.மீ/மணி

**மருந்து தெளிப்பு ஆலோசனை:**
👉 **{spray_suit}**{footer}"""
        elif lang == "mr":
            reply = f"""**थेट हवामान व फवारणी सल्ला ({district})** {icon}

• **सध्याचे तापमान**: {temp}°C | **हवामान**: {cond}
• **हवेतील आर्द्रता**: {hum}% | **वाऱ्याचा वेग**: {wind} किमी/ताਸ

**फवारणी सल्ला:**
👉 **{spray_suit}**
{"⚠️ पाऊस किंवा जोराचा वारा असल्यास फवारणी टाळावी." if wind > 18 or rain > 1.0 else "✅ हवामान खते व कीटकनाशक फवारणीसाठी योग्य आहे."}{footer}"""
        elif lang == "kn":
            reply = f"""**ಲೈವ್ ಹವಾಮಾನ ಮತ್ತು ಸಿಂಪಡಣೆ ಸಲಹೆ ({district})** {icon}

• **ತಾಪಮಾನ**: {temp}°C | **ಸ್ಥಿತಿ**: {cond}
• **ತೇವಾಂಶ**: {hum}% | **ಗಾಳಿಯ ವೇಗ**: {wind} ಕಿಮೀ/ಗಂ

**ಸಿಂಪಡಣೆ ಸಲಹೆ:**
👉 **{spray_suit}**{footer}"""
        elif lang == "bn":
            reply = f"""**লাইভ আবহাওয়া ও স্প্রে পরামর্শ ({district})** {icon}

• **বর্তমান তাপমাত্রা**: {temp}°C | **আবহাওয়া**: {cond}
• **বাতাসে আর্দ্রতা**: {hum}% | **বাতাসের গতি**: {wind} কিমি/ঘণ্টা

**স্প্রে করার পরামর্শ:**
👉 **{spray_suit}**{footer}"""
        elif lang == "gu":
            reply = f"""**લાઇવ હવામાન અને છંટકાવ સલાહ ({district})** {icon}

• **તાપમાન**: {temp}°C | **હવામાન**: {cond}
• **ભેજનું પ્રમાણ**: {hum}% | **પવનની ગતિ**: {wind} કિમી/કલાક

**છંટકાવ સલાહ:**
👉 **{spray_suit}**{footer}"""
        elif lang == "pa":
            reply = f"""**ਲਾਈਵ ਮੌਸਮ ਅਤੇ ਸਪਰੇਅ ਸਲਾਹ ({district})** {icon}

• **ਤਾਪਮਾਨ**: {temp}°C | **ਮੌਸਮ**: {cond}
• **ਨਮੀ**: {hum}% | **ਹਵਾ ਦੀ ਰਫ਼ਤਾਰ**: {wind} ਕਿਮੀ/ਘੰਟਾ

**ਸਪਰੇਅ ਸਲਾਹ:**
👉 **{spray_suit}**{footer}"""
        elif lang == "ur":
            reply = f"""**لائیو موسم اور سپرے کا مشورہ ({district})** {icon}

• **موجودہ درجہ حرارت**: {temp}°C | **موسم**: {cond}
• **نمی کا تناسب**: {hum}% | **ہوا کی رفتار**: {wind} کلومیٹر/گھنٹہ

**سپرے کے لیے مشورہ:**
👉 **{spray_suit}**{footer}"""
        else:
            reply = f"""**Real-Time Agricultural Weather & Spraying Advisory ({district})** {icon}

• **Temperature**: {temp}°C | **Conditions**: {cond}
• **Relative Humidity**: {hum}% | **Wind Speed**: {wind} km/h
• **Precipitation**: {rain} mm

**Spraying Recommendation:**
👉 **{spray_suit}**
{"⚠️ High wind speed or rain detected. Delay foliar spray to avoid drift and wash-off." if wind > 18 or rain > 1.0 else "✅ Current atmospheric conditions are favorable for field spraying and irrigation."}{footer}"""

        return {"reply": reply, "intent": "WEATHER_ADVISORY", "raw_data": weather}

    # 2. CROP DISEASE & PEST MANAGEMENT
    elif any(k in q_lower for k in ["disease", "pest", "blight", "fungus", "yellow", "curl", "thrips", "borer", "कीट", "रोग", "पीले", "తెగులు", "కీటకం", "நோய்", "பூச்சி", "ಕೀಟ", "രോഗം", "পোকা", "રોગ", "ਕੀੜੇ", "روگ", "কীট"]):
        if lang == "hi":
            reply = f"""**{crop} फसल सुरक्षा एवं कीट/रोग प्रबंधन** 🛡️

1. **शुरुआती लक्षण पहचानें**: पत्तियों पर पीले धब्बे या सिकुड़न फफूंद (Fungus) या रसचूसक कीट (Thrips/Aphids) के लक्षण हो सकते हैं।
2. **अनुशंसित प्राथमिक उपचार**:
   • **जैविक उपचार**: 5 मिली नीम का तेल (1500 PPM) प्रति लीटर पानी में मिलाकर सुबह या शाम छिड़कें।
   • **रासायनिक उपचार**: फफूंद जनित रोग के लिए मैन्कोजेब (Mancozeb 75% WP) 2 ग्राम प्रति लीटर पानी।
3. **महत्वपूर्ण सावधानी**:
   • अनुशंसित मात्रा से अधिक रासायनिक दवा न डालें।
   • पूरे खेत में छिड़काव से पहले एक छोटी क्यारी में परीक्षण करें।{footer}"""
        elif lang == "te":
            reply = f"""**{crop} పంట రక్షణ & తెగుళ్ల నివారణ** 🛡️

1. **లక్షణాలు గుర్తించండి**: ఆకులు పసుపు రంగులోకి మారడం లేదా ముడతలు పడటం బూజు లేదా రసం పీల్చే పురుగుల లక్షణం.
2. **నివారణ చర్యలు**:
   • **సేంద్రీయ పద్ధతి**: లీటరు నీటికి 5 మి.లీ వేప నూనె కలిపి ఉదయం లేదా సాయంత్రం పిచಿಕారీ చేయండి.
   • **రసాయన పద్ధతి**: బూజు తెగుళ్లకు మాంకోజెబ్ (Mancozeb 75% WP) 2 గ్రాములు లీటరు నీటికి కలపండి.
3. **ముఖ్య సూచన**: డీలర్లు చెప్పే అధిక మోతాదు మందులను గుడ్డిగా వాడవద్దు.{footer}"""
        elif lang == "mr":
            reply = f"""**{crop} पीक संरक्षण व रोग व्यवस्थापन** 🛡️

1. **लक्षणे ओळखा**: पानांवर पिवळे डाग किंवा पाने वाकडी होणे हे बुरशी किंवा थ्रिप्स किडीचे लक्षण असू शकते.
2. **उपाययोजना**:
   • **सेंद्रिय उपाय**: निंबोळी अर्क किंवा नीम तेल (5 मिली प्रति लिटर पाणी) फवारावे.
   • **रासायनिक उपाय**: बुरशी रोगासाठी मँकोझेब (Mancozeb) 2 ग्रॅम प्रति लिटर पाणी.
3. **काळजी**: फवारणीपूर्वी जमिनीमध्ये पुरेशी ओल असावी.{footer}"""
        else:
            reply = f"""**Crop Health & Pest/Disease Guidance ({crop})** 🛡️

1. **Symptom Identification**: Yellowing or curling leaves typically indicate either sucking pests (Thrips/Aphids) or fungal blight.
2. **Agronomic Treatment Guidelines**:
   • **Preventative / Organic**: Apply Neem Oil formulation (1500 PPM, 5 ml/liter) during early morning or late afternoon.
   • **Fungal Blight**: Use standard Mancozeb 75% WP at 2 g/liter or Copper Oxychloride 50% WP at 2.5 g/liter.
3. **Safety Advice**:
   • Do not exceed recommended concentrations.
   • Avoid spraying during peak afternoon heat or rainfall.{footer}"""

        return {"reply": reply, "intent": "DISEASE_PEST"}

    # 3. GOVERNMENT SCHEMES & MSP
    elif any(k in q_lower for k in ["scheme", "pm kisan", "pm-kisan", "pmfby", "insurance", "msp", "subsidy", "योजना", "बीमा", "పథకం", "திட்டம்", "विमा", "ਯੋਜਨਾ", "ଯୋଜନା", "اسکیم"]):
        if lang == "hi":
            reply = f"""**प्रमुख सरकारी कृषि योजनाएं एवं सहायता** 🏛️

1. **प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)**:
   • पात्र किसानों को प्रति वर्ष ₹6,000 की प्रत्यक्ष वित्तीय सहायता (₹2,000 की 3 किस्तें)।
   • पोर्टल: `pmkisan.gov.in` पर ई-केवाईसी (e-KYC) अनिवार्य है।

2. **प्रधानमंत्री फसल बीमा योजना (PMFBY)**:
   • प्राकृतिक आपदाओं, बेमौसम बारिश या कीट प्रकोप से फसल क्षति पर वित्तीय सुरक्षा।
   • खरीफ फसल के लिए केवल 2% और रबी के लिए 1.5% प्रीमियम।

3. **ई-नाम (e-NAM) डिजिटल मंडी**:
   • राष्ट्रीय स्तर पर अपनी उपज को ऑनलाइन उच्चतम बोली पर बेचने की सुविधा।
   • पोर्टल: `enam.gov.in`{footer}"""
        elif lang == "te":
            reply = f"""**ప్రభుత్వ వ్యవసాయ పథకాలు & మద్దతు** 🏛️

1. **పీఎం కిసాన్ (PM-KISAN)**: అర్హులైన రైతులకు సంవత్సరానికి ₹6,000 ఆర్థిక సహాయం (3 విడతల్లో). పోర్టల్: `pmkisan.gov.in`.
2. **పీఎం ఫసల్ బీమా యోజన (PMFBY)**: పంట నష్టానికి తక్కువ ప్రీమియంతో సమగ్ర పంట బీమా రక్షణ.
3. **ఈ-నామ్ (e-NAM)**: దేశవ్యాప్తంగా వ్యాపారులకు ఆన్‌లైన్‌లో పంటను నేరుగా విక్రయించే సదుపాయం.{footer}"""
        else:
            reply = f"""**Key Government Agricultural Schemes & Farmer Support** 🏛️

1. **PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)**:
   • Direct income support of ₹6,000 per year in 3 equal installments to eligible landholding farmers.
   • Official Portal: `pmkisan.gov.in` (e-KYC required).

2. **PMFBY (Crop Insurance Scheme)**:
   • Comprehensive risk insurance against natural calamities, pests, and unseasonal rainfall.
   • Minimal farmer premium: 2% for Kharif crops and 1.5% for Rabi food/oilseed crops.

3. **e-NAM (National Agriculture Market)**:
   • Pan-India electronic trading portal integrating APMC mandis for transparent price discovery.{footer}"""

        return {"reply": reply, "intent": "GOVERNMENT_SCHEMES"}

    # 4. MASTER SELLING & MARKET REALIZATION QUERIES
    elif any(k in q_lower for k in ["sell", "mandi", "market", "bhav", "price", "बेचूं", "भाव", "अమ్మాలా", "ధర", "விற்க", "விலை", "विकू", "ମଣ୍ଡି", "বিক্রি", "ਵੇਚਣਾ"]):
        mkt_res = analyze_nearby_markets(farmer_lat=lat, farmer_lon=lon, commodity=crop, quantity_quintals=yield_q)
        best_mkt = mkt_res["best_market"]
        price_res = forecast_price_direction(commodity=crop, state=state, market=best_mkt["name"], current_modal_price=best_mkt["modal_price"])
        
        dir_code = price_res["direction_code"]
        rec_action = "SELL 40% / HOLD 60%" if dir_code == "INCREASE" else "SELL IMMEDIATELY"
        
        if lang == "hi":
            reply = f"""**🌾 किसान शील्ड बिक्री सिफ़ारिश ({crop})**

👉 **सिफ़ारिश**: **{rec_action}**
📍 **सर्वोत्तम मंडी**: **{best_mkt['name']}** ({best_mkt['distance_km']} किमी)
• **सकल मंडी भाव**: ₹{best_mkt['modal_price']:,.2f}/क्विंटल
• **अनुमानित भाड़ा व शुल्क**: -₹{best_mkt['total_deductions_per_q']:,.2f}/क्विंटल
• **हाथ में शुद्ध भाव (Net Realization)**: **₹{best_mkt['net_realization_per_q']:,.2f}/क्विंटल**

📈 **7-दिन का भाव रुझान**: **{price_res['direction_label']}** (अनुमानित: {price_res['forecast_range_str']})
🎯 **मॉडल सटीकता**: {price_res['confidence_score_pct']}%

**निर्णय का कारण:**
{best_mkt['name']} मंडी में माल ले जाने पर प्रति क्विंटल सर्वाधिक शुद्ध बचत होगी। 7 दिनों में भाव बढ़ने की संभावना को देखते हुए 40% माल बेचकर लागत निकालें और 60% माल रोकें।{footer}"""
        elif lang == "te":
            reply = f"""**🌾 కిసాన్ షీల్డ్ అమ్మకం సిఫార్సు ({crop})**

👉 **సిఫార్సు**: **{rec_action}**
📍 **ఉత్తమ మార్కెట్**: **{best_mkt['name']}** ({best_mkt['distance_km']} కిమీ)
• **స్థూల ధర**: ₹{best_mkt['modal_price']:,.2f}/క్వింటాల్
• **రవాణా & ఇతర ఖర్చులు**: -₹{best_mkt['total_deductions_per_q']:,.2f}/క్వింటాల్
• **చేతికి వచ్చే నికర ధర**: **₹{best_mkt['net_realization_per_q']:,.2f}/క్వింటాల్**

📈 **7 రోజుల ధర ధోరణి**: **{price_res['direction_label']}** ({price_res['forecast_range_str']})
🎯 **మోడల్ విశ్వసనీయత**: {price_res['confidence_score_pct']}%

**నిర్ణయానికి కారణం:**
ఖర్చులు పోనూ {best_mkt['name']} మార్కెట్‌లో ఎక్కువ నికర లాభం లభిస్తుంది. ధరల పెరుగుదల సంకేతాలు ఉన్నందున 40% అమ్మి మిగిలిన 60% ఉంచండి.{footer}"""
        elif lang == "mr":
            reply = f"""**🌾 किसान शील्ड विक्री निर्णय ({crop})**

👉 **शिफारस**: **{rec_action}**
📍 **उत्तम बाजार समिती**: **{best_mkt['name']}** ({best_mkt['distance_km']} किमी)
• **एकूण भाव**: ₹{best_mkt['modal_price']:,.2f}/क्विंटल
• **वाहतूक व खर्च**: -₹{best_mkt['total_deductions_per_q']:,.2f}/क्विंटल
• **हातात मिळणारा निव्वळ भाव**: **₹{best_mkt['net_realization_per_q']:,.2f}/क्विंटल**

📈 **७ दिवसांचा भाव अंदाज**: **{price_res['direction_label']}** ({price_res['forecast_range_str']})
🎯 **मॉडेल विश्वासार्हता**: {price_res['confidence_score_pct']}%

**निर्णयाचा आधार:**
{best_mkt['name']} येथे वाहतूक खर्च वजा जाता सर्वाधिक निव्वळ परतावा मिळत आहे. भाववाढीचा कल लक्षात घेऊन ४०% माल विका व ६०% साठवून ठेवा.{footer}"""
        elif lang == "ta":
            reply = f"""**🌾 கிசான் ஷீல்ட் விற்பனை பரிந்துரை ({crop})**

👉 **பரிந்துரை**: **{rec_action}**
📍 **சிறந்த சந்தை**: **{best_mkt['name']}** ({best_mkt['distance_km']} கி.மீ)
• **மொத்த விலை**: ₹{best_mkt['modal_price']:,.2f}/குவிண்டால்
• **நிகர வருவாய்**: **₹{best_mkt['net_realization_per_q']:,.2f}/குவிண்டால்**

📈 **7 நாள் விலை போக்கு**: **{price_res['direction_label']}**{footer}"""
        elif lang == "kn":
            reply = f"""**🌾 ಕಿಸಾನ್ ಶೀಲ್ಡ್ ಮಾರಾಟ ಶಿಫಾರಸು ({crop})**

👉 **ಶಿಫಾರಸು**: **{rec_action}**
📍 **ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ**: **{best_mkt['name']}** ({best_mkt['distance_km']} ಕಿಮೀ)
• **ನಿವ್ವಳ ಬೆಲೆ**: **₹{best_mkt['net_realization_per_q']:,.2f}/ಕ್ವಿಂಟಾಲ್**
📈 **7 ದಿನಗಳ ಬೆಲೆ ಪ್ರವೃತ್ತಿ**: **{price_res['direction_label']}**{footer}"""
        elif lang == "bn":
            reply = f"""**🌾 কিসান শিল্ড বিক্রির সিদ্ধান্ত ({crop})**

👉 **পরামর্শ**: **{rec_action}**
📍 **সেরা মণ্ডি**: **{best_mkt['name']}** ({best_mkt['distance_km']} কিমি)
• **হাতে পাওয়া নিট দর**: **₹{best_mkt['net_realization_per_q']:,.2f}/কুইন্টাল**
📈 **৭ দিনের দামের পূর্বাভাস**: **{price_res['direction_label']}**{footer}"""
        elif lang == "gu":
            reply = f"""**🌾 કિસાન શીલ્ડ વેચાણ ભલામણ ({crop})**

👉 **ભલામણ**: **{rec_action}**
📍 **શ્રેષ્ઠ યાર્ડ**: **{best_mkt['name']}** ({best_mkt['distance_km']} કિમી)
• **ચોખ્ખો ભાવ**: **₹{best_mkt['net_realization_per_q']:,.2f}/ક્વિન્ટલ**
📈 **૭ દિવસનું વલણ**: **{price_res['direction_label']}**{footer}"""
        elif lang == "pa":
            reply = f"""**🌾 ਕਿਸਾਨ ਸ਼ੀਲਡ ਵਿਕਰੀ ਸਲਾਹ ({crop})**

👉 **ਸਲਾਹ**: **{rec_action}**
📍 **ਸਭ ਤੋਂ ਵਧੀਆ ਮੰਡੀ**: **{best_mkt['name']}** ({best_mkt['distance_km']} ਕਿਮੀ)
• **ਹੱਥ ਆਉਣ ਵਾਲਾ ਸ਼ੁੱਧ ਭਾਅ**: **₹{best_mkt['net_realization_per_q']:,.2f}/ਕੁਇੰਟਲ**
📈 **੭ ਦਿਨਾਂ ਦਾ ਰੁਝਾਨ**: **{price_res['direction_label']}**{footer}"""
        elif lang == "ur":
            reply = f"""**🌾 کسان شیلڈ فروخت کا مشورہ ({crop})**

👉 **مشورہ**: **{rec_action}**
📍 **بہترین منڈی**: **{best_mkt['name']}** ({best_mkt['distance_km']} کلومیٹر)
• **خالص قیمت**: **₹{best_mkt['net_realization_per_q']:,.2f}/کوئنٹل**
📈 **7 دن کا رجحان**: **{price_res['direction_label']}**{footer}"""
        else:
            reply = f"""**🌾 KisanShield Selling Decision & Market Realization ({crop})**

👉 **Recommendation**: **{rec_action}**
📍 **Best Recommended Mandi**: **{best_mkt['name']}** ({best_mkt['distance_km']} km away)
• **Gross Modal Price**: ₹{best_mkt['modal_price']:,.2f}/quintal
• **Transport & Mandi Deductions**: -₹{best_mkt['total_deductions_per_q']:,.2f}/quintal
• **True Net Realization**: **₹{best_mkt['net_realization_per_q']:,.2f}/quintal**

📈 **7-Day Price Direction**: **{price_res['direction_label']}** (Target: {price_res['forecast_range_str']})
🎯 **Model Directional Confidence**: {price_res['confidence_score_pct']}%

**Rationale:**
Transporting to {best_mkt['name']} yields the highest net pocket realization after accounting for freight costs. Staggered selling (40% now, 60% hold) eliminates downside risk while allowing you to capitalize on predicted price increases.{footer}"""

        return {"reply": reply, "intent": "SELL_DECISION", "raw_data": mkt_res}

    # 5. GENERAL AGRICULTURAL HELP
    else:
        if lang == "hi":
            reply = f"""नमस्ते {farmer_name} जी! मैं आपका **किसान शील्ड AI सहायक** हूँ।

मैं आपकी खेत जानकारी (**{crop}**, **{acres} एकड़**, **{district}, {state}**) से जुड़ा हूँ।

**आप मुझसे पूछ सकते हैं:**
• *"क्या मुझे आज फसल बेचनी चाहिए?"*
• *"नजदीकी मंडी में शुद्ध भाव क्या मिल रहा है?"*
• *"आज छिड़काव के लिए मौसम कैसा रहेगा?"*
• *"फसल में रोग या कीट लगने पर क्या करें?"*{footer}"""
        elif lang == "te":
            reply = f"""నమస్కారం {farmer_name} గారు! నేను మీ **కిసాన్ షీల్డ్ AI సహాయకుడిని**.

మీ పంట సమాచారం (**{crop}**, **{acres} ఎకరాలు**, **{district}, {state}**) నా వద్ద ఉంది.

**మీరు నన్ను ఇలా అడగవచ్చు:**
• *"నేను ఈరోజు పంటను అమ్మాలా?"*
• *"సమీప మార్కెట్లో నికర ధర ఎంత వస్తుంది?"*
• *"ఈరోజు మందుల పిచికారీకి వాతావరణం అనుకూలమా?"*{footer}"""
        elif lang == "mr":
            reply = f"""नमस्कार {farmer_name}! मी आपला **किसान शील्ड AI मदतनीस** आहे.

मी आपल्या शेताशी (**{crop}**, **{acres} एकर**, **{district}, {state}**) जोडलेला आहे.

**आपण विचारू शकता:**
• *"माल आज विकावा की थांबावे?"*
• *"कोणत्या बाजार समितीत सर्वाधिक निव्वळ भाव मिळेल?"*
• *"आज फवारणीसाठी हवामान कसे आहे?"*{footer}"""
        elif lang == "ta":
            reply = f"""வணக்கம் {farmer_name}! நான் உங்கள் **கிசான் ஷீಲ್ட் AI உதவியாளர்**.

உங்கள் பயிர் വിവരங்கள் (**{crop}**, **{district}**).
சந்தை விலை, விற்பனை நேரம், மருந்து தெளிப்பு அல்லது வானிலை பற்றி கேளுங்கள்!{footer}"""
        elif lang == "kn":
            reply = f"""ನಮಸ್ಕಾರ {farmer_name}! ನಾನು ನಿಮ್ಮ **ಕಿಸಾನ್ ಶೀಲ್ಡ್ AI ಸಹಾಯಕ**.
ಮಾರುಕಟ್ಟೆ ಬೆಲೆ, ಮಾರಾಟದ ಸಮಯ, ಕೀಟ ನಿಯಂತ್ರಣ ಅಥವಾ ಹವಾಮಾನದ ಬಗ್ಗೆ ಕೇಳಿ!{footer}"""
        elif lang == "bn":
            reply = f"""নমস্কার {farmer_name}! আমি আপনার **কিসান শিল্ড AI সহকারী**।
মণ্ডি দর, বিক্রির সঠিক সময়, সার-ওষুধ প্রয়োগ বা আবহাওয়া সম্পর্কে জিজ্ঞাসা করুন!{footer}"""
        elif lang == "gu":
            reply = f"""નમસ્તે {farmer_name}! હું તમારો **કિસાન શીલ્ડ AI સહાયક** છું.
યાર્ડના ભાવ, વેચાણનો સમય, દવાનો છંટકાવ અથવા આજના હવામાન વિશે પૂછો!{footer}"""
        elif lang == "pa":
            reply = f"""ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ {farmer_name}! ਮੈਂ ਤੁਹਾਡਾ **ਕਿਸਾਨ ਸ਼ੀਲਡ AI ਸਹਾਇਕ** ਹਾਂ।
ਮੰਡੀ ਭਾਅ, ਵੇਚਣ ਦਾ ਸਮਾਂ, ਖਾਦ ਜਾਂ ਮੌਸਮ ਬਾਰੇ ਪੁੱਛੋ!{footer}"""
        elif lang == "ur":
            reply = f"""سلام {farmer_name}! میں آپ کا **کسان شیلڈ AI مددگار** ہوں۔
منڈی بھاؤ، فروخت کا وقت، کھاد کی صحیح مقدار یا موسم کے بارے میں کچھ بھی پوچھیں!{footer}"""
        else:
            reply = f"""Hello {farmer_name}! I am your **Kishan Shield AI Assistant**.

I am connected to your farm profile (**{crop}**, **{acres} Acres** in **{district}, {state}**).

**Ask me about:**
• *"Should I sell my crop today or wait?"*
• *"Which nearby APMC mandi gives the highest net realization?"*
• *"Is today's weather suitable for chemical spraying?"*
• *"How do I treat blight or leaf curl in my crops?"*{footer}"""

        return {"reply": reply, "intent": "GENERAL_HELP"}
