import os
import pandas as pd
import numpy as np

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FEATURES_DIR = os.path.join(DATA_DIR, "features")
os.makedirs(FEATURES_DIR, exist_ok=True)

def create_features():
    clean_csv = os.path.join(PROCESSED_DIR, "clean_mandi_data.csv")
    if not os.path.exists(clean_csv):
        print(f"Clean mandi data not found at {clean_csv}. Run clean_mandi_data.py first.")
        return
    
    print("Loading clean dataset for feature engineering...")
    # Sample top commodities (e.g. Onion, Tomato, Potato) for robust feature dataset
    df = pd.read_csv(clean_csv, low_memory=False)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort strictly by commodity, state, market, date
    df = df.sort_values(by=['commodity', 'state', 'market', 'date']).reset_index(drop=True)
    
    print("Computing temporal lags, rolling indicators, and arrival momentum...")
    
    # Group by commodity, state, market
    grouped = df.groupby(['commodity', 'state', 'market'])
    
    df['price_lag_1'] = grouped['modal_price'].shift(1)
    df['price_lag_7'] = grouped['modal_price'].shift(7)
    df['price_lag_14'] = grouped['modal_price'].shift(14)
    
    df['price_rolling_7_mean'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(7, min_periods=3).mean())
    df['price_rolling_7_std'] = grouped['modal_price'].transform(lambda x: x.shift(1).rolling(7, min_periods=3).std())
    df['price_volatility_7'] = (df['price_rolling_7_std'] / (df['price_rolling_7_mean'] + 1e-5)) * 100
    
    if 'arrivals' in df.columns:
        df['arrivals_lag_1'] = grouped['arrivals'].shift(1)
        df['arrivals_rolling_7_mean'] = grouped['arrivals'].transform(lambda x: x.shift(1).rolling(7, min_periods=3).mean())
        df['arrival_momentum'] = df['arrivals_lag_1'] - df['arrivals_rolling_7_mean']
    else:
        df['arrivals_lag_1'] = 0.0
        df['arrivals_rolling_7_mean'] = 0.0
        df['arrival_momentum'] = 0.0
        
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.dayofweek
    df['year'] = df['date'].dt.year
    
    # Target definition (7-day ahead price direction)
    df['future_price_7'] = grouped['modal_price'].shift(-7)
    df['price_diff_pct'] = ((df['future_price_7'] - df['modal_price']) / (df['modal_price'] + 1e-5)) * 100
    
    def classify_direction(pct):
        if pd.isna(pct):
            return np.nan
        if pct > 2.5:
            return 1 # INCREASE
        elif pct < -2.5:
            return -1 # DECREASE
        else:
            return 0 # STABLE
            
    df['target_direction'] = df['price_diff_pct'].apply(classify_direction)
    
    # Drop rows with NaN targets or lags
    df_clean = df.dropna(subset=['target_direction', 'price_lag_1', 'price_lag_7']).copy()
    
    out_csv = os.path.join(FEATURES_DIR, "features_mandi_data.csv")
    df_clean.to_csv(out_csv, index=False)
    print(f"Feature engineering complete. Saved {len(df_clean)} records to {out_csv}.")
    
if __name__ == "__main__":
    create_features()
