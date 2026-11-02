import os
import pandas as pd
import json

base_dir = r"c:\Users\hp\Desktop\Kisanapp"

def detailed_audit():
    print("=== DEEP DATA AUDIT ===")
    
    # 1. Yield data
    yield_path = os.path.join(base_dir, "archive (4)", "Crop Yeild Data.csv")
    if os.path.exists(yield_path):
        df_yield = pd.read_csv(yield_path)
        print(f"\n[Crop Yield Data] Rows: {len(df_yield)}, Cols: {list(df_yield.columns)}")
        print(f"Years: {df_yield['Crop_Year'].min()} - {df_yield['Crop_Year'].max()}")
        print(f"Crops ({df_yield['Crop'].nunique()}): {df_yield['Crop'].unique()[:10]}")
        print(f"States ({df_yield['State'].nunique()}): {df_yield['State'].unique()[:10]}")
        print(f"Duplicates: {df_yield.duplicated().sum()}")
    
    # 2. Crop recommendation data
    rec_path = os.path.join(base_dir, "archive (3)", "Crop_recommendation.csv")
    if os.path.exists(rec_path):
        df_rec = pd.read_csv(rec_path)
        print(f"\n[Crop Recommendation Data] Rows: {len(df_rec)}, Cols: {list(df_rec.columns)}")
        print(f"Crops ({df_rec['label'].nunique()}): {df_rec['label'].unique()}")
    
    # 3. Commodity sample (Onion & Tomato) from archive (2)
    for comm in ["Onion.csv", "Tomato.csv", "Potato.csv"]:
        comm_path = os.path.join(base_dir, "archive (2)", comm)
        if os.path.exists(comm_path):
            df_comm = pd.read_csv(comm_path)
            print(f"\n[Commodity: {comm}] Rows: {len(df_comm)}, Cols: {list(df_comm.columns)}")
            print(f"Date Range: {df_comm['Reported Date'].min()} to {df_comm['Reported Date'].max()}")
            print(f"States: {df_comm['State Name'].nunique()}, Markets: {df_comm['Market Name'].nunique()}")
            print(f"Duplicates: {df_comm.duplicated().sum()}")

    # 4. Yearly sample (2023.csv & 2024.csv) from archive (1)
    for yfile in ["2023.csv", "2024.csv"]:
        y_path = os.path.join(base_dir, "archive (1)", "csv", yfile)
        if os.path.exists(y_path):
            df_y = pd.read_csv(y_path, nrows=50000)
            print(f"\n[Yearly Mandi: {yfile}] Sample 50k Rows, Cols: {list(df_y.columns)}")
            print(f"Arrival_Date sample: {df_y['Arrival_Date'].min()} to {df_y['Arrival_Date'].max()}")
            print(f"Commodities sample: {df_y['Commodity'].nunique()}")

if __name__ == "__main__":
    detailed_audit()
