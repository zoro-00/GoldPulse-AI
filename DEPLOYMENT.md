# 🚀 Deployment Guide - Gold Price Prediction System

This guide covers deploying your Gold Price Prediction dashboard to various platforms.

---

## 📦 Docker Deployment (Recommended)

### Prerequisites
- Docker installed
- Docker Compose installed
- Trained models in `models/` directory

### Steps

1. **Build the Docker image:**
```bash
docker build -t gold-price-prediction .
```

2. **Run with Docker Compose:**
```bash
docker-compose up -d
```

This will start:
- Dashboard on `http://localhost:8501`
- Background scheduler for automated monitoring

3. **View logs:**
```bash
# Dashboard logs
docker logs -f gold-price-dashboard

# Scheduler logs
docker logs -f gold-price-scheduler
```

4. **Stop services:**
```bash
docker-compose down
```

### Updating

```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## ☁️ Cloud Deployment Options

### 1. Streamlit Cloud (Free, Easy)

**Best for:** Quick deployment, free tier available

**Steps:**

1. **Push code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/gold-price-prediction
git push -u origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_dashboard.py`
   - Click "Deploy"

3. **Add secrets** (for email config):
   - Go to app settings → Secrets
   - Add:
   ```toml
   [email]
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   sender_email = "your_email@gmail.com"
   sender_password = "your_app_password"
   
   [recipients]
   emails = ["recipient1@example.com", "recipient2@example.com"]
   ```

4. **Update config.py** to use secrets:
```python
import streamlit as st

# In EMAIL_CONFIG
if hasattr(st, 'secrets'):
    EMAIL_CONFIG = {
        'smtp_server': st.secrets["email"]["smtp_server"],
        'smtp_port': st.secrets["email"]["smtp_port"],
        'sender_email': st.secrets["email"]["sender_email"],
        'sender_password': st.secrets["email"]["sender_password"],
        'recipient_emails': st.secrets["recipients"]["emails"]
    }
```

**Limitations:**
- Free tier: 1GB RAM, 1GB storage
- No background scheduler support
- App sleeps after inactivity

---

### 2. AWS Deployment

#### Option A: EC2 Instance

**Steps:**

1. **Launch EC2 instance:**
   - Instance type: t2.micro or t2.small
   - AMI: Ubuntu 22.04 LTS
   - Security group: Open port 8501

2. **Connect and setup:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Clone your repository
git clone https://github.com/yourusername/gold-price-prediction
cd gold-price-prediction

# Install dependencies
pip3 install -r requirements.txt

# Copy your trained models to models/ directory
# (Upload via SCP or train on instance)
```

3. **Run with systemd (persistent):**

Create `/etc/systemd/system/gold-dashboard.service`:
```ini
[Unit]
Description=Gold Price Prediction Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gold-price-prediction
ExecStart=/usr/bin/python3 -m streamlit run streamlit_dashboard.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gold-dashboard
sudo systemctl start gold-dashboard
sudo systemctl status gold-dashboard
```

4. **Setup nginx reverse proxy (optional):**
```bash
sudo apt install nginx -y
```

Create `/etc/nginx/sites-available/gold-dashboard`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/gold-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Option B: AWS Elastic Beanstalk

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize:**
```bash
eb init -p python-3.10 gold-price-prediction
```

3. **Create application:**
```bash
eb create gold-price-env
```

4. **Deploy:**
```bash
eb deploy
```

5. **Open:**
```bash
eb open
```

**Cost:** ~$20-40/month for basic setup

---

### 3. Google Cloud Platform (GCP)

#### Cloud Run (Serverless)

1. **Install gcloud CLI**

2. **Build and push Docker image:**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gold-price-prediction

# Deploy
gcloud run deploy gold-price-dashboard \
  --image gcr.io/YOUR_PROJECT_ID/gold-price-prediction \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```

**Cost:** Pay per use, ~$5-15/month for low traffic

---

### 4. Heroku

1. **Create `Procfile`:**
```
web: streamlit run streamlit_dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create `runtime.txt`:**
```
python-3.10.12
```

3. **Deploy:**
```bash
heroku login
heroku create gold-price-prediction
git push heroku main
heroku open
```

**Note:** Heroku free tier discontinued. Minimum $7/month.

---

### 5. Azure

#### Azure App Service

1. **Install Azure CLI**

2. **Create resource group:**
```bash
az group create --name gold-price-rg --location eastus
```

3. **Create app service plan:**
```bash
az appservice plan create --name gold-price-plan --resource-group gold-price-rg --sku B1 --is-linux
```

4. **Create web app:**
```bash
az webapp create --resource-group gold-price-rg --plan gold-price-plan --name gold-price-dashboard --runtime "PYTHON:3.10"
```

5. **Deploy:**
```bash
az webapp up --name gold-price-dashboard --runtime "PYTHON:3.10"
```

**Cost:** ~$13/month for B1 tier

---

## 🔒 Security Considerations

### 1. Environment Variables

Never commit sensitive data. Use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_CONFIG = {
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
}
```

### 2. HTTPS

Always use HTTPS in production:
- Let's Encrypt for free SSL certificates
- Cloud providers offer managed SSL

### 3. Authentication

Add basic auth to Streamlit:

```python
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Your app code here
    pass
```

### 4. Rate Limiting

Prevent API abuse:

```python
import streamlit as st
from datetime import datetime, timedelta

def check_rate_limit():
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
        return True
    
    time_since_last = datetime.now() - st.session_state.last_refresh
    if time_since_last < timedelta(seconds=60):
        st.warning(f"Please wait {60 - time_since_last.seconds} seconds before refreshing")
        return False
    
    st.session_state.last_refresh = datetime.now()
    return True
```

---

## 📊 Monitoring & Logging

### 1. Application Logs

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler()]
)
```

### 2. Error Tracking

Use Sentry for error tracking:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

### 3. Uptime Monitoring

- **UptimeRobot:** Free monitoring, email/SMS alerts
- **Pingdom:** Professional monitoring
- **Datadog:** Comprehensive monitoring

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Deploy to server
      env:
        SSH_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        SERVER_IP: ${{ secrets.SERVER_IP }}
      run: |
        # Add deployment commands here
        ssh -i $SSH_KEY ubuntu@$SERVER_IP 'cd /app && git pull && systemctl restart gold-dashboard'
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (Basic) | Paid (Production) |
|----------|-----------|--------------|-------------------|
| Streamlit Cloud | ✅ Limited | - | - |
| AWS EC2 | 12 months | $10-20/mo | $50-100/mo |
| GCP Cloud Run | $0-5/mo | $5-15/mo | $20-50/mo |
| Heroku | ❌ | $7/mo | $25-50/mo |
| Azure | ❌ | $13/mo | $50-100/mo |
| DigitalOcean | ❌ | $6/mo | $20-40/mo |

---

## 🆘 Troubleshooting Deployment

### Port already in use
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Out of memory
```bash
# Increase swap on Linux
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Dependencies failing
```bash
# Use specific versions
pip install --no-cache-dir -r requirements.txt
```

---

## 📚 Additional Resources

- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Docker Documentation](https://docs.docker.com/)
- [AWS EC2 Guide](https://docs.aws.amazon.com/ec2/)
- [GCP Cloud Run](https://cloud.google.com/run/docs)
- [nginx Configuration](https://nginx.org/en/docs/)

---

**Need help? Check the main README.md or create an issue on GitHub.**
