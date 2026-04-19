# 🪙 Gold Price Prediction System - Complete Implementation

**ML-driven real-time gold price monitoring and forecasting system for Indian markets**

This implementation extends your XGBoost model with:

- 📊 Interactive Streamlit Dashboard
- 📧 Email Alert System with configurable thresholds
- 🔄 Automated monitoring and reporting
- 📍 State-wise price predictions with GST

---

## 🎯 Features Implemented

### ✅ Dashboard (Streamlit Web UI)

- Real-time gold price display
- Interactive price history charts with EMAs
- 10/30/90-day forecast visualizations
- State-wise price comparison
- Auto-refresh capability
- Configurable alert thresholds

### ✅ Email Alert System

- Threshold-based alerts (upper/lower limits)
- Price change percentage alerts
- Daily summary reports
- HTML-formatted emails
- Rate limiting to avoid spam

### ✅ Automated Monitoring

- Scheduled price checks
- Automated daily summaries
- Logging system
- Error handling and recovery

### ✅ Data Pipeline

- Real-time data fetching from Yahoo Finance
- Feature engineering pipeline
- State-wise price calculations with GST
- Current price tracking

---

## 📁 Project Structure

```
gold-price-prediction/
├── config.py                           # Configuration settings
├── data_pipeline.py                    # Data fetching and preprocessing
├── model_inference.py                  # Model loading and predictions
├── email_alerts.py                     # Email notification system
├── streamlit_dashboard.py              # Main dashboard application
├── scheduler.py                        # Automated monitoring
├── train_and_backtest_model.py         # Retrain + backtest + save artifacts
├── save_models_notebook.py             # Legacy notebook helper
├── requirements.txt                    # Python dependencies
├── models/                             # Saved models (created after training)
│   ├── xgboost_model.pkl
│   ├── feature_columns.pkl
│   ├── model_metadata.json
│   ├── backtest_report.json
│   └── backtest_predictions.csv
└── Gold_Price_Prediction_Phase1_XGBoost.ipynb
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Train and Backtest

Run the retraining script to build the model, evaluate it, and save artifacts:

```bash
python train_and_backtest_model.py
```

This saves:

- `models/xgboost_model.pkl`
- `models/feature_columns.pkl`
- `models/model_metadata.json`
- `models/backtest_report.json`
- `models/backtest_predictions.csv`

### Step 3: Configure Email (Optional)

Edit `config.py` to set up email alerts:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',  # See below for setup
    'recipient_emails': [
        'recipient1@example.com',
        'recipient2@example.com'
    ]
}
```

**For Gmail:**

1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate a new app password for "Mail"
5. Use that password (not your regular password)

### Step 4: Run the Dashboard

```bash
streamlit run streamlit_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Dashboard Features

### Main Dashboard View

1. **Key Metrics Cards**
   - Current price
   - Tomorrow's forecast
   - 30-day forecast
   - 90-day forecast

2. **Alert Status**
   - Real-time threshold monitoring
   - Visual alerts for price conditions

3. **Interactive Charts**
   - Price history with 7-day and 30-day EMAs
   - Forecast visualization for 10/30/90 days
   - State-wise price comparison

4. **Settings Sidebar**
   - Auto-refresh toggle
   - Email alerts enable/disable
   - Threshold configuration
   - Manual refresh button
   - Test email button

### Using the Dashboard

1. **Monitor Current Prices**
   - View real-time gold prices
   - Check prediction accuracy
   - See trend indicators

2. **Configure Alerts**
   - Set upper/lower price thresholds
   - Configure price change percentage alerts
   - Enable email notifications

3. **Analyze Trends**
   - View historical price charts
   - Compare 7-day vs 30-day EMAs
   - Check forecast trends

4. **State Comparison**
   - See state-wise prices with GST
   - Identify cheapest and costliest states
   - Download detailed state data

---

## 📧 Email Alerts

### Alert Types

1. **High Price Alert**
   - Triggered when price exceeds upper threshold
   - Shows current price, threshold, and prediction

2. **Low Price Alert**
   - Triggered when price falls below lower threshold
   - Indicates potential buying opportunity

3. **Price Change Alert**
   - Triggered when price changes by configured percentage
   - Shows direction and magnitude of change

4. **Daily Summary**
   - Sent at scheduled time (default: 9 AM)
   - Includes current price, predictions, top/bottom states

### Configuring Alerts

In `config.py`:

```python
ALERT_THRESHOLDS = {
    'price_change_percent': 2.0,  # Alert if price changes by 2%
    'price_upper_limit': 65000,   # Alert if price > ₹65,000/10g
    'price_lower_limit': 55000,   # Alert if price < ₹55,000/10g
    'volatility_threshold': 1.5,
}
```

### Testing Email Setup

```python
from email_alerts import EmailAlertSystem

# Test your configuration
alert_system = EmailAlertSystem()
alert_system.test_connection()
```

Or use the "Test Email" button in the dashboard sidebar.

---

## 🤖 Automated Monitoring

### Running the Scheduler

For continuous monitoring with automated emails:

```bash
python scheduler.py
```

This will:

- Check prices every hour
- Send daily summary at 9:00 AM
- Log all activities to `gold_price_monitor.log`

### Customizing the Schedule

Edit `scheduler.py`:

```python
# Check prices every 30 minutes
schedule.every(30).minutes.do(monitor.check_prices)

# Daily summary at 6 PM
schedule.every().day.at("18:00").do(monitor.send_daily_summary)

# Weekly summary on Monday at 9 AM
schedule.every().monday.at("09:00").do(monitor.send_weekly_summary)
```

### Running as Background Service

**On Linux/Mac:**

```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

**On Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Action: Start a program
4. Program: `python`
5. Arguments: `scheduler.py`
6. Start in: `C:\path\to\your\project`

---

## 🔧 Configuration Reference

### `config.py` Settings

```python
# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',
    'recipient_emails': ['recipient@example.com']
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    'price_change_percent': 2.0,
    'price_upper_limit': 65000,
    'price_lower_limit': 55000,
    'volatility_threshold': 1.5,
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'refresh_interval': 300,  # seconds
    'page_title': '🪙 Gold Price Prediction Dashboard',
    'page_icon': '🪙',
    'layout': 'wide',
    'forecast_horizons': [10, 30, 90],
}

# Data Configuration
DATA_CONFIG = {
    'tickers': {
        'gold': 'GC=F',
        'usd_inr': 'USDINR=X',
        'crude_oil': 'CL=F',
        'nifty': '^NSEI'
    },
    'lookback_days': 730,
    'gst_rate': 0.03,
}
```

---

## 📈 API Reference

### GoldDataPipeline

```python
from data_pipeline import GoldDataPipeline

pipeline = GoldDataPipeline()

# Fetch latest data
latest, df = pipeline.get_latest_features()

# Get current price
current = pipeline.get_current_price()

# Calculate state prices
state_prices = pipeline.calculate_state_prices(base_price_inr_10g)
```

### GoldPricePredictor

```python
from model_inference import GoldPricePredictor

predictor = GoldPricePredictor()
predictor.load_models()

# Next day prediction
next_day_price = predictor.predict_next_day(features_df)

# Multi-horizon forecast
predictions = predictor.get_predictions_summary(features_df)
# Returns: {'next_day': ..., '10day': ..., '30day': ..., '90day': ...}

# Recursive forecast
forecast_90 = predictor.recursive_forecast(features_df, horizon_days=90)
```

### EmailAlertSystem

```python
from email_alerts import EmailAlertSystem

alert_system = EmailAlertSystem()

# Test connection
alert_system.test_connection()

# Check thresholds and send alerts
alerts = alert_system.check_and_alert(
    current_price=60000,
    predicted_price=61000,
    previous_price=59000
)

# Send daily summary
alert_system.send_daily_summary(current_price, predictions, state_prices)
```

---

## 🎓 Model Training Workflow

1. **Data Collection**
   - Yahoo Finance API for historical data
   - GoldAPI.io for real-time prices (optional)

2. **Feature Engineering**
   - Log returns for stationarity
   - Lag features (1, 3, 7 days)
   - EMAs (7-day, 30-day)
   - Ratios and volatility

3. **Model Training**
   - Linear Regression (baseline)
   - Random Forest
   - XGBoost (final model)

4. **Model Evaluation**
   - RMSE, MAE, R²
   - Train-test split (chronological)
   - Cross-validation

5. **Save Models**
   - Use `save_models_notebook.py` code
   - Creates `models/` directory with pickle files

---

## 🐛 Troubleshooting

### Models Not Found

**Error:** `Models not found. Please train and save models first.`

**Solution:**

1. Run your notebook completely
2. Add the save models code at the end
3. Verify `models/` directory contains 3 .pkl files

### Email Not Sending

**Error:** `Failed to send email. Check configuration.`

**Solutions:**

1. **Gmail:** Use app-specific password, not regular password
2. **2FA:** Must be enabled for app passwords
3. **Firewall:** Allow outbound SMTP (port 587)
4. **Test:** Use the "Test Email" button in dashboard

### Data Fetch Errors

**Error:** `Error fetching data from Yahoo Finance`

**Solutions:**

1. Check internet connection
2. Verify ticker symbols in `config.py`
3. Yahoo Finance API might be temporarily down
4. Try again after a few minutes

### Dashboard Not Loading

**Solutions:**

1. Check if Streamlit is installed: `pip install streamlit`
2. Run from correct directory containing all files
3. Check port 8501 is not in use
4. Try different port: `streamlit run streamlit_dashboard.py --server.port 8502`

---

## 📊 State-wise Price Calculation

Formula used:

```
State Price = Base Price × (1 + GST) × (1 + State Factor)

Where:
- Base Price = Gold price in INR/10g
- GST = 3% (0.03)
- State Factor = ±2% based on transport costs and regional demand
```

Example for Maharashtra (factor = 0.015):

```
If Base Price = ₹60,000
State Price = 60,000 × 1.03 × 1.015 = ₹62,742
```

---

## 🔐 Security Best Practices

1. **Email Credentials**
   - Never commit passwords to git
   - Use environment variables:

   ```python
   import os
   EMAIL_CONFIG['sender_password'] = os.environ.get('EMAIL_PASSWORD')
   ```

2. **API Keys**
   - Store in `.env` file
   - Add `.env` to `.gitignore`
   - Use python-dotenv:

   ```bash
   pip install python-dotenv
   ```

3. **Model Files**
   - Keep models in secure location
   - Regular backups
   - Version control with DVC

---

## 📝 Next Steps / Future Enhancements

### Suggested Improvements

1. **Data Sources**
   - [ ] Integrate GoldAPI.io for real-time prices
   - [ ] Add RBI announcements scraper
   - [ ] Include geopolitical news sentiment

2. **Models**
   - [ ] Implement LSTM for sequence modeling
   - [ ] Ensemble multiple models
   - [ ] Add confidence intervals

3. **Dashboard**
   - [ ] Add user authentication
   - [ ] Historical alert logs
   - [ ] Downloadable reports (PDF/Excel)
   - [ ] Mobile responsive design

4. **Alerts**
   - [ ] SMS notifications via Twilio
   - [ ] Telegram bot integration
   - [ ] Slack webhooks

5. **Deployment**
   - [ ] Docker containerization
   - [ ] Deploy to cloud (AWS/GCP/Azure)
   - [ ] Set up CI/CD pipeline

---

## 📚 References

- **Base Paper:** Gold Price Prediction System Using ML and Real-Time Data Analysis for Indian Markets - IJSCI Vol.3, Issue 2, Feb 2026
- **Yahoo Finance API:** https://python-yahoofinance.readthedocs.io/
- **XGBoost Documentation:** https://xgboost.readthedocs.io/
- **Streamlit Documentation:** https://docs.streamlit.io/

---

## 👥 Authors

- **Students:** BT23CSE177 Rishi Shahu | BT23CSE187 Priyanshu Gupta
- **Course:** Mini Project | ML Lab | CA-1

---

## 📄 License

This project is for educational purposes as part of the Mini Project coursework.

---

## 🆘 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the configuration settings
3. Check log files for detailed error messages
4. Consult the base notebook for model details

---

**Happy Predicting! 🪙📈**
