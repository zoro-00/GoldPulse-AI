# ⚡ Quick Start Guide

Get your Gold Price Prediction Dashboard running in 5 minutes!

---

## 📋 Prerequisites

- Python 3.8 or higher
- Your trained XGBoost model from the notebook
- Internet connection

---

## 🚀 3-Step Setup

### Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

### Step 2: Train and Backtest (2 minutes)

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

### Step 3: Launch Dashboard (30 seconds)

```bash
streamlit run streamlit_dashboard.py
```

Dashboard opens at: `http://localhost:8501`

---

## ✅ That's It!

You should now see:

- 📊 Real-time gold prices
- 📈 Price forecasts (10/30/90 days)
- 📍 State-wise price comparison
- ⚙️ Configurable alert thresholds

---

## 🎯 What You Get

### Dashboard Features

- **Live Price Monitoring** - Current gold price in INR/10g
- **Smart Predictions** - Next-day and long-term forecasts
- **State Comparison** - Prices across all Indian states
- **Auto-Refresh** - Optional automatic data updates
- **Alert System** - Visual threshold indicators

### In the Sidebar

- 🔄 Auto-refresh toggle
- 📧 Email alerts (optional)
- ⚙️ Threshold configuration
- 🔄 Manual refresh button

---

## 📧 Email Alerts (Optional - 2 minutes)

1. Edit `config.py`:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',  # ← Change this
    'sender_password': 'your_app_password',  # ← Change this
    'recipient_emails': ['recipient@example.com']  # ← Change this
}
```

2. For Gmail:
   - Go to: https://myaccount.google.com/apppasswords
   - Generate app password
   - Use that (not your regular password)

3. Test in dashboard:
   - Click "Test Email" button in sidebar

---

## 🤖 Automated Monitoring (Optional)

Want automated price checks and email reports?

```bash
python scheduler.py
```

This runs in background and:

- ✅ Checks prices every hour
- ✅ Sends daily summary at 9 AM
- ✅ Logs everything to `gold_price_monitor.log`

---

## 🧪 Test Your Setup

```bash
python test_system.py
```

This validates:

- ✅ All packages installed
- ✅ Models loaded correctly
- ✅ Data pipeline working
- ✅ Email configured (if enabled)

---

## 🆘 Quick Troubleshooting

### Models Not Found?

```bash
# Check if models exist
ls models/

# Should see:
# xgboost_model.pkl
# feature_columns.pkl
# model_metadata.json
```

If missing → Go back to Step 2

### Can't Send Email?

- Using Gmail app password (not regular password)?
- 2-factor auth enabled?
- Check firewall allows port 587

### Dashboard Won't Start?

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall Streamlit
pip install --upgrade streamlit

# Try different port
streamlit run streamlit_dashboard.py --server.port 8502
```

---

## 📖 Need More Help?

- **Full Documentation:** See `README.md`
- **Deployment Guide:** See `DEPLOYMENT.md`
- **Configuration:** Edit `config.py`

---

## 🎉 Pro Tips

1. **Bookmark the Dashboard**
   - Add to browser favorites for quick access

2. **Mobile Access**
   - Dashboard works on mobile browsers
   - Get your local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Access from phone: `http://your-ip:8501`

3. **Auto-Start on Boot**
   - See `DEPLOYMENT.md` for systemd setup (Linux)
   - Or use Task Scheduler (Windows)

4. **Customize Thresholds**
   - Adjust in sidebar based on your strategy
   - Settings persist during session

5. **Export Data**
   - Use the expandable state prices table
   - Copy data for your analysis

---

## 🚀 Next Level

Want to deploy publicly?

```bash
# Quick deploy to Streamlit Cloud (Free)
git init
git add .
git commit -m "Initial commit"
git push

# Then: share.streamlit.io → Deploy
```

See `DEPLOYMENT.md` for cloud deployment options.

---

**Happy Trading! 🪙📈**

_Built with ❤️ for ML Lab CA-1_
