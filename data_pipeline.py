"""
Data Pipeline for Gold Price Prediction System
Handles real-time data fetching, preprocessing, and feature engineering
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from config import DATA_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldDataPipeline:
    """Pipeline for fetching and processing gold price data"""
    
    def __init__(self):
        self.tickers = DATA_CONFIG['tickers']
        self.lookback_days = DATA_CONFIG['lookback_days']
        self.gst_rate = DATA_CONFIG['gst_rate']
        
    def fetch_latest_data(self):
        """Fetch latest data from Yahoo Finance"""
        try:
            logger.info("Fetching latest market data...")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.lookback_days)
            
            # Fetch all tickers
            data = {}
            for name, ticker in self.tickers.items():
                df = yf.download(ticker, start=start_date, end=end_date, progress=False)
                close_data = df['Close']
                if isinstance(close_data, pd.DataFrame):
                    close_data = close_data.iloc[:, 0]
                data[name] = close_data
                logger.info(f"Fetched {len(df)} records for {name} ({ticker})")
            
            # Combine into single dataframe
            df = pd.DataFrame(data)
            df.columns = ['Gold_USD_oz', 'USDINR', 'Crude_Oil', 'Nifty50']
            
            # Remove any rows with missing data
            df = df.ffill().dropna()
            
            logger.info(f"Combined dataset: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def engineer_features(self, df):
        """Apply feature engineering pipeline"""
        df = df.copy()
        
        # Convert Gold from USD/oz to INR/10g
        df['Gold_INR_10g'] = (df['Gold_USD_oz'] / 31.1035) * 10 * df['USDINR']
        
        # Returns (log returns for stationarity)
        df['Gold_Return'] = np.log(df['Gold_INR_10g'] / df['Gold_INR_10g'].shift(1))
        df['USDINR_Return'] = np.log(df['USDINR'] / df['USDINR'].shift(1))
        df['Oil_Return'] = np.log(df['Crude_Oil'] / df['Crude_Oil'].shift(1))
        df['Nifty_Return'] = np.log(df['Nifty50'] / df['Nifty50'].shift(1))
        
        # Lag features (1, 3, 7 days)
        for lag in [1, 3, 7]:
            df[f'Gold_Lag_{lag}'] = df['Gold_Return'].shift(lag)
            df[f'USDINR_Lag_{lag}'] = df['USDINR_Return'].shift(lag)
        
        # Exponential Moving Averages
        df['Gold_EMA_7'] = df['Gold_INR_10g'].ewm(span=7, adjust=False).mean()
        df['Gold_EMA_30'] = df['Gold_INR_10g'].ewm(span=30, adjust=False).mean()
        
        # Ratios
        df['Gold_EMA_Ratio'] = df['Gold_EMA_7'] / df['Gold_EMA_30']
        df['Gold_Oil_Ratio'] = df['Gold_INR_10g'] / df['Crude_Oil']
        
        # Volatility (7-day rolling std of returns)
        df['Gold_Volatility'] = df['Gold_Return'].rolling(window=7).std()
        
        # Target: Next day gold price
        df['Target'] = df['Gold_INR_10g'].shift(-1)
        
        # Drop NaN rows
        df = df.dropna()
        
        logger.info(f"Features engineered. Final shape: {df.shape}")
        return df
    
    def get_latest_features(self):
        """Get the latest row with all features for prediction"""
        df = self.fetch_latest_data()
        df_features = self.engineer_features(df)
        
        # Get the most recent complete row
        latest = df_features.iloc[-1]
        
        return latest, df_features
    
    def calculate_state_prices(self, base_price_inr_10g):
        """Calculate state-wise prices with GST and regional factors"""
        from config import STATE_FACTORS
        
        state_prices = {}
        base_with_gst = base_price_inr_10g * (1 + self.gst_rate)
        
        for state, factor in STATE_FACTORS.items():
            state_prices[state] = base_with_gst * (1 + factor)
        
        return state_prices
    
    def get_current_price(self):
        """Get current gold price"""
        try:
            ticker = yf.Ticker(self.tickers['gold'])
            hist = ticker.history(period='1d')
            
            if len(hist) > 0:
                gold_usd_oz = hist['Close'].iloc[-1]
                
                # Get current USD/INR
                usd_inr_ticker = yf.Ticker(self.tickers['usd_inr'])
                usd_inr_hist = usd_inr_ticker.history(period='1d')
                usd_inr = usd_inr_hist['Close'].iloc[-1] if len(usd_inr_hist) > 0 else 83.0
                
                # Convert to INR/10g
                gold_inr_10g = (gold_usd_oz / 31.1035) * 10 * usd_inr
                
                return {
                    'gold_usd_oz': gold_usd_oz,
                    'usd_inr': usd_inr,
                    'gold_inr_10g': gold_inr_10g,
                    'timestamp': datetime.now()
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None


if __name__ == "__main__":
    # Test the pipeline
    pipeline = GoldDataPipeline()
    
    print("Testing data pipeline...")
    latest, df = pipeline.get_latest_features()
    print(f"\nLatest features shape: {latest.shape}")
    print(f"Latest Gold price (INR/10g): ₹{latest['Gold_INR_10g']:.2f}")
    
    current = pipeline.get_current_price()
    if current:
        print(f"\nCurrent price:")
        print(f"  Gold (USD/oz): ${current['gold_usd_oz']:.2f}")
        print(f"  USD/INR: ₹{current['usd_inr']:.2f}")
        print(f"  Gold (INR/10g): ₹{current['gold_inr_10g']:.2f}")
