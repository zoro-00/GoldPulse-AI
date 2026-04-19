"""
Configuration file for Gold Price Prediction System
"""

# Email Configuration (Mailtrap)
EMAIL_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,  # or 587
    'sender_email': '56d42be5dfed33',  # Mailtrap username
    'sender_password': '77feac60f59604',  # Mailtrap password
    'recipient_emails': [
        'test@example.com'
    ]
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    'price_change_percent': 2.0,  # Alert if price changes by 2% or more
    'price_upper_limit': 65000,   # Alert if price goes above this (INR/10g)
    'price_lower_limit': 55000,   # Alert if price goes below this (INR/10g)
    'volatility_threshold': 1.5,  # Alert if volatility increases by this factor
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'refresh_interval': 300,  # Refresh data every 5 minutes (300 seconds)
    'page_title': '🪙 Gold Price Prediction Dashboard',
    'page_icon': '🪙',
    'layout': 'wide',
    'forecast_horizons': [10, 30, 90],  # Days to forecast
}

# Data Configuration
DATA_CONFIG = {
    'tickers': {
        'gold': 'GC=F',
        'usd_inr': 'USDINR=X',
        'crude_oil': 'CL=F',
        'nifty': '^NSEI'
    },
    'lookback_days': 730,  # 2 years of historical data
    'gst_rate': 0.03,  # 3% GST
}

# State-wise factors (±2% for transport costs and regional demand)
STATE_FACTORS = {
    'Maharashtra': 0.015,
    'Karnataka': 0.010,
    'Tamil Nadu': 0.012,
    'Kerala': 0.018,
    'West Bengal': 0.020,
    'Gujarat': 0.008,
    'Rajasthan': 0.005,
    'Delhi': 0.010,
    'Uttar Pradesh': 0.015,
    'Madhya Pradesh': 0.012,
    'Andhra Pradesh': 0.013,
    'Telangana': 0.014,
    'Punjab': 0.009,
    'Haryana': 0.010,
    'Bihar': 0.020,
    'Odisha': 0.018,
    'Assam': 0.022,
    'Chhattisgarh': 0.016,
    'Jharkhand': 0.019,
    'Uttarakhand': 0.011,
}

# Model paths
MODEL_PATHS = {
    'xgboost': 'models/xgboost_model.pkl',
    'scaler': 'models/scaler.pkl',
    'feature_columns': 'models/feature_columns.pkl'
}

# Manual forecast override for dashboard display.
FORECAST_OVERRIDE = {
    'enabled': True,
    'next_day': 142268.74,
    '10day': 146138.92,
    '30day': 155044.75,
    '90day': 185072.31,
}
