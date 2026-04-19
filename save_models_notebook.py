"""
Add this code cell at the end of your Gold_Price_Prediction notebook
to save the trained models for use in the dashboard
"""

# ============================================================
# SAVE MODELS FOR DASHBOARD
# ============================================================

import os
import pickle
import sys


def _resolve_variable(candidates, globals_dict):
    """Return the first available variable from the notebook globals."""
    for name in candidates:
        if name in globals_dict and globals_dict[name] is not None:
            return globals_dict[name]
    return None

print("Saving models for dashboard...")

nb_globals = globals()

# Try common variable names used in notebooks.
xgb_model = _resolve_variable(["xgb_model", "model", "best_model"], nb_globals)
feature_columns = _resolve_variable(["feature_columns"], nb_globals)

if feature_columns is None and "X_train" in nb_globals:
    x_train = nb_globals["X_train"]
    if hasattr(x_train, "columns"):
        feature_columns = x_train.columns.tolist()

missing = []
if xgb_model is None:
    missing.append("xgb_model")
if feature_columns is None:
    missing.append("feature_columns or X_train.columns")

if missing:
    model_path = "models/xgboost_model.pkl"
    features_path = "models/feature_columns.pkl"
    existing_model = os.path.exists(model_path) and os.path.getsize(model_path) > 0
    existing_features = os.path.exists(features_path) and os.path.getsize(features_path) > 0
    if existing_model and existing_features:
        print("Using existing model artifacts from models/ folder.")
        print("Found: models/xgboost_model.pkl and models/feature_columns.pkl")
        sys.exit(0)

    print(
        "Missing required notebook variables: "
        + ", ".join(missing)
        + ". Run this after training in the notebook where those variables exist."
    )
    print("Tip: Execute this code as the final cell in your training notebook.")
    sys.exit(1)

os.makedirs("models", exist_ok=True)

with open("models/xgboost_model.pkl", "wb") as f:
    pickle.dump(xgb_model, f)
print("✅ XGBoost model saved")

with open("models/feature_columns.pkl", "wb") as f:
    pickle.dump(feature_columns, f)
print("✅ Feature columns saved")

print("\n" + "="*50)
print("All models saved successfully!")
print("You can now run the dashboard: streamlit run streamlit_dashboard.py")
print("="*50)

# Verify what was saved
print("\nSaved feature columns:")
print(feature_columns)
