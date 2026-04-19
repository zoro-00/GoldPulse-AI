"""
Model Inference for Gold Price Prediction
Loads trained models and makes predictions
"""

import pickle
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from config import MODEL_PATHS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldPricePredictor:
    """Prediction engine using trained XGBoost model"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.target_type = None
        self.forecast_mode = None
        self.loaded = False
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load XGBoost model
            with open(MODEL_PATHS['xgboost'], 'rb') as f:
                self.model = pickle.load(f)
            logger.info("XGBoost model loaded successfully")
            
            # Scaler is not used in the retrained pipeline.
            self.scaler = None
            
            # Load feature columns
            with open(MODEL_PATHS['feature_columns'], 'rb') as f:
                self.feature_columns = pickle.load(f)
            logger.info(f"Feature columns loaded: {len(self.feature_columns)} features")

            # Load optional metadata describing how the model target was trained.
            metadata_path = 'models/model_metadata.json'
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                self.target_type = metadata.get('target_type')
                self.forecast_mode = metadata.get('forecast_mode')
                logger.info(f"Model metadata loaded: target_type={self.target_type}")
                logger.info(f"Forecast mode loaded: {self.forecast_mode}")
            
            self.loaded = True
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            logger.info("Please train and save the models first using the notebook")
            return False
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def predict_next_day(self, features_df):
        """Predict next day's gold price"""
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first")
        
        # Get the latest row
        latest = features_df.iloc[[-1]]

        current_price = float(latest['Gold_INR_10g'].values[0])

        if self.forecast_mode == 'baseline':
            return self._baseline_forecast_price(features_df, current_price)
        
        # Select and order features
        X = latest[self.feature_columns]
        
        # Scale features only when a scaler is explicitly present.
        model_input = self.scaler.transform(X) if self.scaler is not None else X

        predicted_value = float(self.model.predict(model_input)[0])
        if not np.isfinite(predicted_value):
            raise ValueError("Model prediction is not finite")

        if self.target_type == 'return':
            predicted_price = current_price * np.exp(predicted_value)
        elif self.target_type == 'price':
            predicted_price = predicted_value
        else:
            # Backward compatibility for older model artifacts.
            if abs(predicted_value) < 5:
                predicted_price = current_price * np.exp(predicted_value)
            else:
                predicted_price = predicted_value

        if (not np.isfinite(predicted_price)) or predicted_price <= 0:
            raise ValueError("Predicted price is invalid")

        return float(predicted_price)

    def _baseline_return_signal(self, features_df):
        """Estimate a short-horizon return from recent price momentum."""
        recent_returns = features_df['Gold_Return'].tail(7).dropna()
        if recent_returns.empty:
            return 0.0

        mean_return = float(recent_returns.mean())
        last_return = float(recent_returns.iloc[-1])
        volatility = float(recent_returns.std(ddof=0)) if len(recent_returns) > 1 else 0.0

        # Blend mean and momentum, then damp extreme moves.
        signal = 0.6 * mean_return + 0.4 * last_return
        signal = float(np.clip(signal, -0.03, 0.03))

        # If the recent series is very noisy, shrink the signal.
        if volatility > 0.02:
            signal *= 0.5

        return signal

    def _baseline_forecast_price(self, features_df, current_price):
        """Trend-based fallback forecast when the learned model underperforms."""
        predicted_return = self._baseline_return_signal(features_df)
        predicted_price = current_price * np.exp(predicted_return)
        return float(max(predicted_price, 0.01))
    
    def recursive_forecast(self, features_df, horizon_days):
        """
        Recursively forecast gold prices for multiple days ahead
        
        Args:
            features_df: DataFrame with historical data and features
            horizon_days: Number of days to forecast (e.g., 10, 30, 90)
        
        Returns:
            List of predicted prices for each day
        """
        if not self.loaded:
            raise RuntimeError("Models not loaded. Call load_models() first")
        
        predictions = []
        df = features_df.copy()
        
        for day in range(horizon_days):
            # Predict next day
            predicted_price = self.predict_next_day(df)
            predictions.append(predicted_price)
            
            # Update dataframe for next iteration
            # Get last row
            last_row = df.iloc[-1].copy()
            current_price = last_row['Gold_INR_10g']
            
            # Calculate return
            predicted_return = np.log(predicted_price / current_price)
            
            # Update values for next day
            new_row = last_row.copy()
            new_row['Gold_INR_10g'] = predicted_price
            new_row['Gold_Return'] = predicted_return
            
            # Update lags (shift everything)
            if 'Gold_Lag_7' in new_row:
                new_row['Gold_Lag_7'] = last_row['Gold_Lag_3']
            if 'Gold_Lag_3' in new_row:
                new_row['Gold_Lag_3'] = last_row['Gold_Lag_1']
            if 'Gold_Lag_1' in new_row:
                new_row['Gold_Lag_1'] = predicted_return
            
            # Update EMAs (exponential moving averages)
            if 'Gold_EMA_7' in new_row:
                alpha_7 = 2 / (7 + 1)
                new_row['Gold_EMA_7'] = alpha_7 * predicted_price + (1 - alpha_7) * last_row['Gold_EMA_7']
            
            if 'Gold_EMA_30' in new_row:
                alpha_30 = 2 / (30 + 1)
                new_row['Gold_EMA_30'] = alpha_30 * predicted_price + (1 - alpha_30) * last_row['Gold_EMA_30']
            
            # Update EMA ratio
            if 'Gold_EMA_Ratio' in new_row and new_row['Gold_EMA_30'] != 0:
                new_row['Gold_EMA_Ratio'] = new_row['Gold_EMA_7'] / new_row['Gold_EMA_30']
            
            # Append new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        return predictions
    
    def get_predictions_summary(self, features_df):
        """Get predictions for standard horizons (10, 30, 90 days)"""
        predictions = {}
        
        # Next day prediction
        predictions['next_day'] = self.predict_next_day(features_df)
        
        # 10-day forecast
        forecast_10 = self.recursive_forecast(features_df, 10)
        predictions['10day'] = forecast_10[-1]
        predictions['10day_series'] = forecast_10
        
        # 30-day forecast
        forecast_30 = self.recursive_forecast(features_df, 30)
        predictions['30day'] = forecast_30[-1]
        predictions['30day_series'] = forecast_30
        
        # 90-day forecast
        forecast_90 = self.recursive_forecast(features_df, 90)
        predictions['90day'] = forecast_90[-1]
        predictions['90day_series'] = forecast_90
        
        return predictions
    
    def calculate_confidence_interval(self, predictions, confidence=0.95):
        """
        Calculate confidence intervals for predictions
        Based on historical prediction errors
        """
        # This is a simplified version
        # In production, you'd use historical validation errors
        std_error = np.std(predictions) * 0.1  # 10% of std as error estimate
        z_score = 1.96  # for 95% confidence
        
        ci_lower = [p - (z_score * std_error) for p in predictions]
        ci_upper = [p + (z_score * std_error) for p in predictions]
        
        return ci_lower, ci_upper


class ModelTrainer:
    """Helper class to save models from notebook"""
    
    @staticmethod
    def save_models(xgb_model, scaler=None, feature_columns=None):
        """
        Save trained models to disk
        Call this from your notebook after training
        
        Example usage in notebook:
            from model_inference import ModelTrainer
            ModelTrainer.save_models(xgb_model, scaler, feature_columns)
        """
        import os

        if feature_columns is None:
            raise ValueError("feature_columns is required")
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Save XGBoost model
        with open(MODEL_PATHS['xgboost'], 'wb') as f:
            pickle.dump(xgb_model, f)
        logger.info(f"XGBoost model saved to {MODEL_PATHS['xgboost']}")
        
        # Save scaler only if provided.
        if scaler is not None:
            with open(MODEL_PATHS['scaler'], 'wb') as f:
                pickle.dump(scaler, f)
            logger.info(f"Scaler saved to {MODEL_PATHS['scaler']}")
        else:
            logger.info("Scaler not provided. Skipping scaler save.")
        
        # Save feature columns
        with open(MODEL_PATHS['feature_columns'], 'wb') as f:
            pickle.dump(feature_columns, f)
        logger.info(f"Feature columns saved to {MODEL_PATHS['feature_columns']}")
        
        print("✅ All models saved successfully!")


if __name__ == "__main__":
    # Test the predictor
    print("Testing model predictor...")
    print("Note: This requires trained models to be saved first.")
    print("Run your notebook and use ModelTrainer.save_models() to save the models.")
