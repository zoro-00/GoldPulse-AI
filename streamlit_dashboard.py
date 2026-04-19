"""
🪙 Gold Price Prediction Dashboard
Streamlit web application for real-time gold price monitoring and predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

from data_pipeline import GoldDataPipeline
from model_inference import GoldPricePredictor
from email_alerts import EmailAlertSystem
from config import DASHBOARD_CONFIG, ALERT_THRESHOLDS, STATE_FACTORS, FORECAST_OVERRIDE

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_CONFIG['page_title'],
    page_icon=DASHBOARD_CONFIG['page_icon'],
    layout=DASHBOARD_CONFIG['layout'],
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976d2;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: 600;
        color: #1f2937;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #d32f2f;
        color: #7f1d1d;
    }
    .alert-low {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        color: #0c4a6e;
    }
    .alert-success {
        background-color: #e8f5e9;
        border-left: 4px solid #388e3c;
        color: #14532d;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = GoldDataPipeline()
if 'predictor' not in st.session_state:
    st.session_state.predictor = GoldPricePredictor()
if 'alert_system' not in st.session_state:
    st.session_state.alert_system = EmailAlertSystem()
if 'last_price' not in st.session_state:
    st.session_state.last_price = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


@st.cache_data(ttl=DASHBOARD_CONFIG['refresh_interval'])
def load_data():
    """Load and process data (cached for performance)"""
    pipeline = st.session_state.pipeline
    latest, df = pipeline.get_latest_features()
    return latest, df


@st.cache_resource
def load_models():
    """Load ML models (cached across sessions)"""
    predictor = GoldPricePredictor()
    success = predictor.load_models()
    if success:
        st.session_state.predictor = predictor
    return predictor, success


def create_price_chart(df):
    """Create interactive price history chart"""
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Gold_INR_10g'],
        mode='lines',
        name='Gold Price',
        line=dict(color='#FFD700', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> ₹%{y:,.2f}<extra></extra>'
    ))
    
    # Add EMA lines
    if 'Gold_EMA_7' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Gold_EMA_7'],
            mode='lines',
            name='7-Day EMA',
            line=dict(color='#FF6B6B', width=1, dash='dash'),
            hovertemplate='<b>7-Day EMA:</b> ₹%{y:,.2f}<extra></extra>'
        ))
    
    if 'Gold_EMA_30' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Gold_EMA_30'],
            mode='lines',
            name='30-Day EMA',
            line=dict(color='#4ECDC4', width=1, dash='dash'),
            hovertemplate='<b>30-Day EMA:</b> ₹%{y:,.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Gold Price History (INR/10g)',
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_forecast_chart(current_price, predictions):
    """Create forecast visualization"""
    # Create dates for forecast
    today = datetime.now()
    dates_10 = [today + timedelta(days=i) for i in range(1, 11)]
    dates_30 = [today + timedelta(days=i) for i in range(1, 31)]
    dates_90 = [today + timedelta(days=i) for i in range(1, 91)]
    
    fig = go.Figure()
    
    # Current price point
    fig.add_trace(go.Scatter(
        x=[today],
        y=[current_price],
        mode='markers',
        name='Current Price',
        marker=dict(size=15, color='#FFD700'),
        hovertemplate='<b>Current:</b> ₹%{y:,.2f}<extra></extra>'
    ))
    
    # 10-day forecast
    if '10day_series' in predictions:
        fig.add_trace(go.Scatter(
            x=dates_10,
            y=predictions['10day_series'],
            mode='lines+markers',
            name='10-Day Forecast',
            line=dict(color='#4CAF50', width=2),
            hovertemplate='<b>10-Day:</b> ₹%{y:,.2f}<extra></extra>'
        ))
    
    # 30-day forecast
    if '30day_series' in predictions:
        fig.add_trace(go.Scatter(
            x=dates_30,
            y=predictions['30day_series'],
            mode='lines',
            name='30-Day Forecast',
            line=dict(color='#2196F3', width=2),
            hovertemplate='<b>30-Day:</b> ₹%{y:,.2f}<extra></extra>'
        ))
    
    # 90-day forecast
    if '90day_series' in predictions:
        fig.add_trace(go.Scatter(
            x=dates_90,
            y=predictions['90day_series'],
            mode='lines',
            name='90-Day Forecast',
            line=dict(color='#FF9800', width=2),
            hovertemplate='<b>90-Day:</b> ₹%{y:,.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Price Forecast',
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_state_map(state_prices):
    """Create state-wise price comparison"""
    df_states = pd.DataFrame([
        {'State': state, 'Price': price}
        for state, price in state_prices.items()
    ]).sort_values('Price', ascending=False)
    
    fig = px.bar(
        df_states,
        x='Price',
        y='State',
        orientation='h',
        title='State-wise Gold Prices (INR/10g)',
        color='Price',
        color_continuous_scale='RdYlGn_r',
        text='Price'
    )
    
    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
    fig.update_layout(height=600, template='plotly_white')
    
    return fig


def _linear_series(start_value, end_value, length):
    """Build a simple linear bridge between two values."""
    if length <= 1:
        return [float(end_value)]

    return np.linspace(float(start_value), float(end_value), num=length).tolist()


def apply_forecast_override(predictions):
    """Replace model forecasts with configured values when override is enabled."""
    if not FORECAST_OVERRIDE.get('enabled', False):
        return predictions

    next_day = float(FORECAST_OVERRIDE['next_day'])
    day_10 = float(FORECAST_OVERRIDE['10day'])
    day_30 = float(FORECAST_OVERRIDE['30day'])
    day_90 = float(FORECAST_OVERRIDE['90day'])

    overridden = dict(predictions)
    overridden['next_day'] = next_day
    overridden['10day'] = day_10
    overridden['30day'] = day_30
    overridden['90day'] = day_90
    overridden['10day_series'] = _linear_series(next_day, day_10, 10)
    overridden['30day_series'] = _linear_series(next_day, day_30, 30)
    overridden['90day_series'] = _linear_series(next_day, day_90, 90)
    return overridden


def main():
    # Header
    st.title("🪙 Gold Price Prediction Dashboard")
    st.markdown("**Real-time ML-driven gold price monitoring and forecasting for Indian markets**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto Refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=60,
                max_value=600,
                value=300,
                step=60
            )
        
        # Email alerts toggle
        email_enabled = st.checkbox("Enable Email Alerts", value=False)
        
        # Threshold settings
        st.subheader("Alert Thresholds")
        price_upper = st.number_input(
            "Upper Threshold (₹/10g)",
            value=ALERT_THRESHOLDS['price_upper_limit'],
            step=1000
        )
        price_lower = st.number_input(
            "Lower Threshold (₹/10g)",
            value=ALERT_THRESHOLDS['price_lower_limit'],
            step=1000
        )
        change_percent = st.slider(
            "Price Change Alert (%)",
            min_value=0.5,
            max_value=5.0,
            value=ALERT_THRESHOLDS['price_change_percent'],
            step=0.5
        )
        
        # Update thresholds
        ALERT_THRESHOLDS['price_upper_limit'] = price_upper
        ALERT_THRESHOLDS['price_lower_limit'] = price_lower
        ALERT_THRESHOLDS['price_change_percent'] = change_percent
        
        st.divider()
        
        # Manual refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Test email button
        if email_enabled:
            if st.button("📧 Test Email"):
                with st.spinner("Sending test email..."):
                    success = st.session_state.alert_system.test_connection()
                    if success:
                        st.success("Test email sent!")
                    else:
                        st.error("Failed to send email. Check configuration.")
    
    # Main content
    try:
        # Load models
        if not st.session_state.data_loaded:
            with st.spinner("Loading models..."):
                predictor, success = load_models()
                if not success:
                    st.error("❌ Models not found. Please train and save models using the notebook first.")
                    st.info("""
                    **To save models from your notebook, add this code at the end:**
                    ```python
                    from model_inference import ModelTrainer
                    
                    # scaler is optional
                    ModelTrainer.save_models(xgb_model, feature_columns=feature_columns.tolist())
                    ```
                    """)
                    return
                st.session_state.data_loaded = True
        
        # Load data
        with st.spinner("Fetching latest data..."):
            latest, df = load_data()
        
        current_price = latest['Gold_INR_10g']
        current_time = datetime.now()
        
        # Get predictions
        with st.spinner("Generating predictions..."):
            predictor = st.session_state.predictor
            if not predictor.loaded:
                if not predictor.load_models():
                    st.error("❌ Models could not be loaded. Please re-save model files and refresh.")
                    return
            predictions = predictor.get_predictions_summary(df)
            predictions = apply_forecast_override(predictions)
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Price (₹/10g)",
                value=f"₹{current_price:,.2f}",
                delta=f"{((current_price - st.session_state.last_price) / st.session_state.last_price * 100):.2f}%" if st.session_state.last_price else None
            )
        
        with col2:
            st.metric(
                label="Tomorrow's Forecast",
                value=f"₹{predictions['next_day']:,.2f}",
                delta=f"{((predictions['next_day'] - current_price) / current_price * 100):.2f}%"
            )
        
        with col3:
            st.metric(
                label="30-Day Forecast",
                value=f"₹{predictions['30day']:,.2f}",
                delta=f"{((predictions['30day'] - current_price) / current_price * 100):.2f}%"
            )
        
        with col4:
            st.metric(
                label="90-Day Forecast",
                value=f"₹{predictions['90day']:,.2f}",
                delta=f"{((predictions['90day'] - current_price) / current_price * 100):.2f}%"
            )
        
        # Alert Status
        st.divider()
        
        # Check thresholds
        alerts = []
        if current_price > ALERT_THRESHOLDS['price_upper_limit']:
            alerts.append(('high', f"⚠️ Price above upper threshold (₹{ALERT_THRESHOLDS['price_upper_limit']:,.0f})"))
        if current_price < ALERT_THRESHOLDS['price_lower_limit']:
            alerts.append(('low', f"💡 Price below lower threshold (₹{ALERT_THRESHOLDS['price_lower_limit']:,.0f})"))
        
        if alerts:
            for alert_type, message in alerts:
                st.markdown(
                    f'<div class="alert-box alert-{alert_type}">{message}</div>',
                    unsafe_allow_html=True
                )
                
                # Send email if enabled
                if email_enabled:
                    st.session_state.alert_system.check_and_alert(
                        current_price,
                        predictions['next_day'],
                        st.session_state.last_price
                    )
        else:
            st.markdown(
                '<div class="alert-box alert-success">✅ All systems normal</div>',
                unsafe_allow_html=True
            )
        
        # Charts
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                create_price_chart(df.tail(180)),  # Last 6 months
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_forecast_chart(current_price, predictions),
                use_container_width=True
            )
        
        # State-wise prices
        st.divider()
        st.subheader("📍 State-wise Gold Prices")
        
        state_prices = st.session_state.pipeline.calculate_state_prices(current_price)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(
                create_state_map(state_prices),
                use_container_width=True
            )
        
        with col2:
            st.markdown("**Top 5 Costliest States**")
            sorted_states = sorted(state_prices.items(), key=lambda x: x[1], reverse=True)
            for state, price in sorted_states[:5]:
                st.markdown(f"**{state}:** ₹{price:,.2f}")
            
            st.markdown("**Top 5 Cheapest States**")
            for state, price in sorted_states[-5:]:
                st.markdown(f"**{state}:** ₹{price:,.2f}")
        
        # Data table
        st.divider()
        with st.expander("📊 View Detailed State Prices"):
            df_states = pd.DataFrame([
                {'State': state, 'Price (₹/10g)': f"₹{price:,.2f}"}
                for state, price in sorted(state_prices.items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(df_states, use_container_width=True, hide_index=True)
        
        # Update last price
        st.session_state.last_price = current_price
        
        # Last updated timestamp
        st.caption(f"Last updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
