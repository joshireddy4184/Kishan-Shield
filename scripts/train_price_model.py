import os
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, mean_absolute_error, mean_squared_error

BASE_DIR = r"c:\Users\hp\Desktop\Kisanapp"
DATA_DIR = os.path.join(BASE_DIR, "data")
FEATURES_DIR = os.path.join(DATA_DIR, "features")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_evaluate():
    features_csv = os.path.join(FEATURES_DIR, "features_mandi_data.csv")
    if not os.path.exists(features_csv):
        print(f"Features file not found at {features_csv}. Using sampled dataset.")
        return
        
    print("Loading engineered features dataset...")
    df = pd.read_csv(features_csv, low_memory=False)
    
    # Feature columns
    feature_cols = [
        'modal_price', 'min_price', 'max_price', 'price_lag_1', 'price_lag_7', 'price_lag_14',
        'price_rolling_7_mean', 'price_volatility_7', 'arrivals_lag_1', 'arrivals_rolling_7_mean',
        'arrival_momentum', 'month', 'quarter', 'day_of_week'
    ]
    
    # Fill missing values in features
    for col in feature_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
            
    # CHRONOLOGICAL SPLIT TO PREVENT DATA LEAKAGE
    print("Performing Chronological Split (Train: <=2021, Val: 2022, Test: >=2023)...")
    
    train_mask = df['year'] <= 2021
    val_mask = df['year'] == 2022
    test_mask = df['year'] >= 2023
    
    # If years are outside bounds, fallback to quantile split chronologically
    if df[test_mask].empty or df[train_mask].empty:
        df = df.sort_values(by='date').reset_index(drop=True)
        n = len(df)
        train_df = df.iloc[:int(n*0.7)]
        val_df = df.iloc[int(n*0.7):int(n*0.85)]
        test_df = df.iloc[int(n*0.85):]
    else:
        train_df = df[train_mask]
        val_df = df[val_mask]
        test_df = df[test_mask]
        
    print(f"Train size: {len(train_df)}, Val size: {len(val_df)}, Test size: {len(test_df)}")
    
    X_train, y_train_dir, y_train_reg = train_df[feature_cols], train_df['target_direction'], train_df['future_price_7']
    X_val, y_val_dir, y_val_reg = val_df[feature_cols], val_df['target_direction'], val_df['future_price_7']
    X_test, y_test_dir, y_test_reg = test_df[feature_cols], test_df['target_direction'], test_df['future_price_7']
    
    # Train Classification Model (Price Direction: -1=DECREASE, 0=STABLE, 1=INCREASE)
    print("Training Random Forest Classifier for 7-day Price Direction...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train_dir)
    
    # Train Regression Model (7-day Future Price)
    print("Training Random Forest Regressor for 7-day Target Price Range...")
    reg = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    reg.fit(X_train, y_train_reg)
    
    # Evaluate on Test Set
    test_preds_dir = clf.predict(X_test)
    test_preds_reg = reg.predict(X_test)
    
    acc = accuracy_score(y_test_dir, test_preds_dir)
    prec = precision_score(y_test_dir, test_preds_dir, average='macro', zero_division=0)
    rec = recall_score(y_test_dir, test_preds_dir, average='macro', zero_division=0)
    
    mae = mean_absolute_error(y_test_reg, test_preds_reg)
    rmse = np.sqrt(mean_squared_error(y_test_reg, test_preds_reg))
    
    print("\n--- MODEL PERFORMANCE EVALUATION (TEST SET) ---")
    print(f"Directional Accuracy: {acc*100:.2f}%")
    print(f"Macro Precision:     {prec:.4f}")
    print(f"Macro Recall:        {rec:.4f}")
    print(f"Target Price MAE:    ₹{mae:.2f}/quintal")
    print(f"Target Price RMSE:   ₹{rmse:.2f}/quintal")
    
    # Save artifacts
    joblib.dump(clf, os.path.join(MODELS_DIR, "price_direction_model.pkl"))
    joblib.dump(reg, os.path.join(MODELS_DIR, "price_forecast_model.pkl"))
    
    importances = dict(zip(feature_cols, clf.feature_importances_.tolist()))
    
    metrics = {
        "model_name": "RandomForest Ensemble (Direction + Regressor)",
        "chronological_split": "Train <=2021, Val 2022, Test >=2023",
        "test_directional_accuracy_pct": round(acc * 100, 2),
        "test_precision": round(prec, 4),
        "test_recall": round(rec, 4),
        "test_mae_rs_per_q": round(float(mae), 2),
        "test_rmse_rs_per_q": round(float(rmse), 2),
        "feature_importances": importances,
        "feature_cols": feature_cols
    }
    
    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\nModels and metrics successfully saved to {MODELS_DIR}")

if __name__ == "__main__":
    train_and_evaluate()
