import os
import pandas as pd
import numpy as np
import glob

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def preprocess_mandi_data():
    print("Preparing Mandi Dataset for ML training...")
    
    # We load primary commodities: Onion, Tomato, Potato, Wheat, Rice, Bajra, Maize, Cotton, Bengal Gram
    target_commodities = ["Onion.csv", "Tomato.csv", "Potato.csv", "Wheat.csv", "Maize.csv"]
    combined_dfs = []
    
    for filename in target_commodities:
        file_path = os.path.join(BASE_DIR, "archive (2)", filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        
        print(f"Loading {filename}...")
        # Read dataset
        df = pd.read_csv(file_path, low_memory=False)
        
        # Standardize column names
        col_map = {
            'State Name': 'state',
            'District Name': 'district',
            'Market Name': 'market',
            'Variety': 'variety',
            'Group': 'group',
            'Arrivals (Tonnes)': 'arrivals',
            'Arrivals': 'arrivals',
            'Min Price (Rs./Quintal)': 'min_price',
            'Min Price': 'min_price',
            'Max Price (Rs./Quintal)': 'max_price',
            'Max Price': 'max_price',
            'Modal Price (Rs./Quintal)': 'modal_price',
            'Modal Price': 'modal_price',
            'Reported Date': 'date'
        }
        df = df.rename(columns=col_map)
        
        # Add commodity name if missing
        commodity_name = filename.replace('.csv', '')
        df['commodity'] = commodity_name
        
        # Keep relevant columns
        cols = ['state', 'district', 'market', 'commodity', 'variety', 'arrivals', 'min_price', 'max_price', 'modal_price', 'date']
        cols_present = [c for c in cols if c in df.columns]
        df = df[cols_present]
        
        # Convert date
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date', 'modal_price'])
        
        # Clean numeric fields
        for col in ['min_price', 'max_price', 'modal_price', 'arrivals']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Deduplicate
        dedup_cols = ['state', 'district', 'market', 'commodity', 'date']
        dedup_cols = [c for c in dedup_cols if c in df.columns]
        df = df.drop_duplicates(subset=dedup_cols)
        
        combined_dfs.append(df)
        print(f"Processed {filename}: {len(df)} clean records.")
    
    if combined_dfs:
        full_df = pd.concat(combined_dfs, ignore_index=True)
        full_df = full_df.sort_values(by=['commodity', 'state', 'market', 'date'])
        
        out_csv = os.path.join(PROCESSED_DIR, "clean_mandi_data.csv")
        full_df.to_csv(out_csv, index=False)
        print(f"\nSaved combined clean dataset to {out_csv} ({len(full_df)} total records).")
        return full_df
    return None

if __name__ == "__main__":
    preprocess_mandi_data()
