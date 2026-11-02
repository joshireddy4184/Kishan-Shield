import os
import glob
import pandas as pd
import json

base_dir = r"c:\Users\hp\Desktop\Kisanapp"

def audit_datasets():
    print("=== KISANSHIELD DATASET AUDIT START ===")
    archives = ["archive (1)", "archive (2)", "archive (3)", "archive (4)", "archive (5)"]
    audit_results = {}

    for arch in archives:
        arch_path = os.path.join(base_dir, arch)
        if not os.path.exists(arch_path):
            continue
        
        csv_files = []
        for root, dirs, files in os.walk(arch_path):
            for file in files:
                if file.endswith('.csv') or file.endswith('.parquet') or file.endswith('.xlsx'):
                    csv_files.append(os.path.join(root, file))
        
        print(f"\n--- {arch} --- (Total structured files found: {len(csv_files)})")
        
        sample_files = csv_files[:5] if len(csv_files) > 5 else csv_files
        for filepath in sample_files:
            filename = os.path.basename(filepath)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"\nFile: {filename} ({size_mb:.2f} MB)")
            try:
                if filepath.endswith('.csv'):
                    df = pd.read_csv(filepath, nrows=1000)
                    total_rows_approx = "1000+ (sampled)"
                elif filepath.endswith('.parquet'):
                    df = pd.read_parquet(filepath)
                    total_rows_approx = len(df)
                else:
                    df = pd.read_excel(filepath, nrows=1000)
                    total_rows_approx = "1000+ (sampled)"
                
                cols = list(df.columns)
                dtypes = {col: str(df[col].dtype) for col in cols}
                null_pct = {col: round(df[col].isnull().mean() * 100, 2) for col in cols}
                
                print(f"  Cols ({len(cols)}): {cols}")
                print(f"  Sample row: {df.iloc[0].to_dict() if not df.empty else 'Empty'}")
                print(f"  Missing %: {null_pct}")
                
            except Exception as e:
                print(f"  Error reading {filename}: {e}")

if __name__ == "__main__":
    audit_datasets()
