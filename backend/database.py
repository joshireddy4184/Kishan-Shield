import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
DB_PATH = os.path.join(BASE_DIR, "kisanshield.db")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    village = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    preferred_language = Column(String(20), default="English")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farms = relationship("Farm", back_populates="farmer")

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    land_area_acres = Column(Float, nullable=False)
    crop = Column(String(50), nullable=False)
    crop_variety = Column(String(50), nullable=True)
    crop_stage = Column(String(50), nullable=True) # Sowing, Vegetative, Flowering, Harvest-Ready
    expected_harvest_quintals = Column(Float, nullable=False)
    expected_harvest_date = Column(String(20), nullable=True)
    irrigation_type = Column(String(50), nullable=True)
    soil_type = Column(String(50), nullable=True)
    money_invested_rs = Column(Float, default=0.0)
    expected_additional_cost_rs = Column(Float, default=0.0)

    farmer = relationship("Farmer", back_populates="farms")
    decisions = relationship("FarmDecision", back_populates="farm")

class AdviceAnalysis(Base):
    __tablename__ = "advice_analyses"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    source_type = Column(String(50)) # WhatsApp, Dealer, YouTube, Social Media, AI
    raw_text = Column(Text)
    extracted_crop = Column(String(50))
    extracted_input = Column(String(100))
    extracted_quantity = Column(String(50))
    trust_score = Column(Integer) # 0-100
    risk_level = Column(String(20)) # LOW, MEDIUM, HIGH
    evidence_strength = Column(String(50))
    source_reliability = Column(String(50))
    commercial_bias_risk = Column(String(50))
    reasons_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class InputPurchase(Base):
    __tablename__ = "input_purchases"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    product_name = Column(String(100))
    input_type = Column(String(50)) # Fertilizer, Pesticide, Seed
    purchased_quantity_kg = Column(Float)
    unit_price_rs = Column(Float)
    total_spent_rs = Column(Float)
    seller_name = Column(String(100))
    recommended_qty_kg = Column(Float)
    potential_excess_kg = Column(Float)
    avoidable_expenditure_rs = Column(Float)
    quantity_risk = Column(String(20))
    reasons_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Market(Base):
    __tablename__ = "markets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    market_type = Column(String(50), default="APMC") # APMC, e-NAM, Regulated
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_km = Column(Float, default=0.0)

class MarketPrice(Base):
    __tablename__ = "market_prices"
    id = Column(Integer, primary_key=True, index=True)
    market_name = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    commodity = Column(String(50), nullable=False)
    min_price = Column(Float)
    modal_price = Column(Float)
    max_price = Column(Float)
    arrivals_tonnes = Column(Float)
    reported_date = Column(String(20))
    source_type = Column(String(20), default="OFFICIAL") # OFFICIAL, CACHED, DEMO

class PolicyEvent(Base):
    __tablename__ = "policy_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    commodity = Column(String(50))
    policy_type = Column(String(50)) # Export Restriction, MSP Update, Procurement, Import Tariff
    official_source = Column(String(100))
    announcement_date = Column(String(20))
    impact_summary = Column(Text)
    market_price_pressure = Column(String(20)) # UPWARD, DOWNWARD, STABLE

class TradeEvent(Base):
    __tablename__ = "trade_events"
    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String(50))
    signal_type = Column(String(50)) # Export Ban, Tariff Increase, Global Shortage
    global_trend = Column(String(100))
    possible_impact = Column(Text)
    domestic_price_effect = Column(String(20))

class FarmDecision(Base):
    __tablename__ = "farm_decisions"
    id = Column(Integer, primary_key=True, index=True)
    passport_code = Column(String(50), unique=True) # e.g. DECISION #027
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    crop = Column(String(50))
    recommended_action = Column(String(50)) # SELL NOW, WAIT, SELL PARTIALLY, SWITCH MARKET
    sell_ratio_pct = Column(Float, default=100.0)
    advice_risk_score = Column(Integer)
    input_risk_score = Column(Integer)
    financial_risk = Column(String(20))
    best_market_name = Column(String(100))
    best_market_net_realization = Column(Float)
    price_forecast_direction = Column(String(20))
    overall_confidence_pct = Column(Float)
    financial_protection_rs = Column(Float)
    assumptions_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="decisions")

class FarmerMemory(Base):
    __tablename__ = "farmer_memories"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    season_year = Column(String(20))
    crop = Column(String(50))
    decision_taken = Column(String(50))
    expected_price = Column(Float)
    actual_realized_price = Column(Float)
    profit_loss_rs = Column(Float)
    historical_learning = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
