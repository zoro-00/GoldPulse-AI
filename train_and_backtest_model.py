#!/usr/bin/env python3
"""Train and backtest the gold price model.

This script trains an XGBoost regressor on next-day return targets, converts
predictions back to prices for evaluation, and saves the resulting artifacts
for the dashboard.
"""

from __future__ import annotations

import json
import os
import pickle
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from xgboost import XGBRegressor

from data_pipeline import GoldDataPipeline


MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_columns.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")
BACKTEST_PATH = os.path.join(MODEL_DIR, "backtest_predictions.csv")
REPORT_PATH = os.path.join(MODEL_DIR, "backtest_report.json")


@dataclass
class Metrics:
    mae: float
    rmse: float
    mape: float
    r2: float
    direction_accuracy: float
    baseline_mae: float
    baseline_rmse: float


def build_dataset() -> pd.DataFrame:
    pipeline = GoldDataPipeline()
    raw = pipeline.fetch_latest_data()
    df = pipeline.engineer_features(raw)
    df = df.copy()
    df["Target_Return"] = np.log(df["Target"] / df["Gold_INR_10g"])
    return df


def make_feature_frame(df: pd.DataFrame):
    feature_columns = [column for column in df.columns if column not in {"Target", "Target_Return"}]
    X = df[feature_columns]
    y_return = df["Target_Return"]
    y_price = df["Target"]
    return feature_columns, X, y_return, y_price


def price_predictions_from_returns(X: pd.DataFrame, return_predictions: np.ndarray) -> np.ndarray:
    current_prices = X["Gold_INR_10g"].to_numpy(dtype=float)
    return current_prices * np.exp(return_predictions)


def evaluate_prices(y_true: pd.Series, y_pred: np.ndarray, baseline_pred: np.ndarray, previous_prices: np.ndarray) -> Metrics:
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mape = float(np.mean(np.abs((y_true.to_numpy(dtype=float) - y_pred) / y_true.to_numpy(dtype=float))) * 100)
    r2 = float(r2_score(y_true, y_pred))
    direction_true = np.sign(y_true.to_numpy(dtype=float) - previous_prices)
    direction_pred = np.sign(y_pred - previous_prices)
    direction_accuracy = float(np.mean(direction_true == direction_pred) * 100)
    baseline_mae = float(mean_absolute_error(y_true, baseline_pred))
    baseline_rmse = float(np.sqrt(mean_squared_error(y_true, baseline_pred)))
    return Metrics(mae, rmse, mape, r2, direction_accuracy, baseline_mae, baseline_rmse)


def train_candidate(X_train, y_train, X_val, y_val, params):
    model = XGBRegressor(
        objective="reg:squarederror",
        random_state=42,
        tree_method="hist",
        n_jobs=-1,
        eval_metric="mae",
        **params,
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    return model


def grid_search(X_train, y_train):
    candidates = [
        {"n_estimators": 300, "max_depth": 2, "learning_rate": 0.03, "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 1},
        {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.03, "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 1},
        {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9, "colsample_bytree": 0.9, "min_child_weight": 1},
        {"n_estimators": 700, "max_depth": 4, "learning_rate": 0.03, "subsample": 0.9, "colsample_bytree": 0.9, "min_child_weight": 2},
        {"n_estimators": 700, "max_depth": 4, "learning_rate": 0.05, "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 2},
    ]

    splitter = TimeSeriesSplit(n_splits=5)
    best_params = None
    best_score = float("inf")

    for params in candidates:
        fold_scores = []
        for train_index, val_index in splitter.split(X_train):
            fold_X_train = X_train.iloc[train_index]
            fold_y_train = y_train.iloc[train_index]
            fold_X_val = X_train.iloc[val_index]
            fold_y_val = y_train.iloc[val_index]

            model = train_candidate(fold_X_train, fold_y_train, fold_X_val, fold_y_val, params)
            pred_returns = model.predict(fold_X_val)
            pred_prices = price_predictions_from_returns(fold_X_val, pred_returns)
            fold_scores.append(mean_absolute_error(fold_y_val, pred_prices))

        score = float(np.mean(fold_scores))
        print(f"Candidate {params} -> CV MAE: {score:,.2f}")
        if score < best_score:
            best_score = score
            best_params = params

    return best_params, best_score


def main():
    print("Building training dataset...")
    df = build_dataset()
    feature_columns, X, y_return, y_price = make_feature_frame(df)

    X_train, X_test, y_train_return, y_test_return, y_train_price, y_test_price = train_test_split(
        X, y_return, y_price, test_size=0.2, shuffle=False
    )

    previous_prices_test = X_test["Gold_INR_10g"].to_numpy(dtype=float)
    baseline_pred = previous_prices_test.copy()

    print("Searching for a better model configuration...")
    best_params, cv_mae = grid_search(X_train, y_train_return)
    print(f"Best params: {best_params}")
    print(f"Best CV MAE: {cv_mae:,.2f}")

    # Keep the last part of the training window for early stopping.
    validation_size = max(20, int(len(X_train) * 0.15))
    final_X_train = X_train.iloc[:-validation_size]
    final_y_train = y_train_return.iloc[:-validation_size]
    final_X_val = X_train.iloc[-validation_size:]
    final_y_val = y_train_return.iloc[-validation_size:]

    final_model = train_candidate(final_X_train, final_y_train, final_X_val, final_y_val, best_params)

    test_return_predictions = final_model.predict(X_test)
    test_price_predictions = price_predictions_from_returns(X_test, test_return_predictions)
    test_metrics = evaluate_prices(y_test_price, test_price_predictions, baseline_pred, previous_prices_test)

    print("\nBacktest results on holdout set:")
    print(f"  MAE: {test_metrics.mae:,.2f}")
    print(f"  RMSE: {test_metrics.rmse:,.2f}")
    print(f"  MAPE: {test_metrics.mape:,.2f}%")
    print(f"  R2: {test_metrics.r2:.4f}")
    print(f"  Direction accuracy: {test_metrics.direction_accuracy:.2f}%")
    print(f"  Baseline MAE (naive hold-last-price): {test_metrics.baseline_mae:,.2f}")
    print(f"  Baseline RMSE: {test_metrics.baseline_rmse:,.2f}")

    forecast_mode = "baseline" if test_metrics.mae >= test_metrics.baseline_mae else "model"
    print(f"  Forecast mode selected: {forecast_mode}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(final_model, f)
    with open(FEATURES_PATH, "wb") as f:
        pickle.dump(feature_columns, f)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "target_type": "return",
                "target_column": "Target_Return",
                "prediction_unit": "price",
                "feature_count": len(feature_columns),
                "best_params": best_params,
                "cv_mae": cv_mae,
                "forecast_mode": forecast_mode,
                "test_metrics": asdict(test_metrics),
            },
            f,
            indent=2,
        )

    backtest_df = pd.DataFrame(
        {
            "actual_price": y_test_price.to_numpy(dtype=float),
            "predicted_price": test_price_predictions,
            "baseline_price": baseline_pred,
            "predicted_return": test_return_predictions,
            "actual_return": y_test_return.to_numpy(dtype=float),
        },
        index=X_test.index,
    )
    backtest_df.to_csv(BACKTEST_PATH, index=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(test_metrics), f, indent=2)

    print("\nSaved artifacts:")
    print(f"  {MODEL_PATH}")
    print(f"  {FEATURES_PATH}")
    print(f"  {METADATA_PATH}")
    print(f"  {BACKTEST_PATH}")
    print(f"  {REPORT_PATH}")


if __name__ == "__main__":
    main()