"""
Automated Scheduler for Gold Price Monitoring
Runs periodic checks and sends email alerts/reports
"""

import schedule
import time
import logging
from datetime import datetime

from data_pipeline import GoldDataPipeline
from model_inference import GoldPricePredictor
from email_alerts import EmailAlertSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gold_price_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GoldPriceMonitor:
    """Automated monitoring system"""
    
    def __init__(self):
        self.pipeline = GoldDataPipeline()
        self.predictor = GoldPricePredictor()
        self.alert_system = EmailAlertSystem()
        self.last_price = None
        
        # Load models
        logger.info("Loading models...")
        if not self.predictor.load_models():
            raise RuntimeError("Failed to load models")
        logger.info("Models loaded successfully")
    
    def check_prices(self):
        """Check current prices and send alerts if needed"""
        try:
            logger.info("Starting price check...")
            
            # Get latest data
            latest, df = self.pipeline.get_latest_features()
            current_price = latest['Gold_INR_10g']
            
            # Get predictions
            predictions = self.predictor.get_predictions_summary(df)
            
            logger.info(f"Current price: ₹{current_price:,.2f}")
            logger.info(f"Predicted price (next day): ₹{predictions['next_day']:,.2f}")
            
            # Check thresholds and send alerts
            alerts = self.alert_system.check_and_alert(
                current_price,
                predictions['next_day'],
                self.last_price
            )
            
            if alerts:
                logger.info(f"Alerts sent: {', '.join(alerts)}")
            else:
                logger.info("No alerts triggered")
            
            # Update last price
            self.last_price = current_price
            
            logger.info("Price check completed")
            
        except Exception as e:
            logger.error(f"Error during price check: {e}", exc_info=True)
    
    def send_daily_summary(self):
        """Send daily summary report"""
        try:
            logger.info("Generating daily summary...")
            
            # Get latest data
            latest, df = self.pipeline.get_latest_features()
            current_price = latest['Gold_INR_10g']
            
            # Get predictions
            predictions = self.predictor.get_predictions_summary(df)
            
            # Calculate state prices
            state_prices = self.pipeline.calculate_state_prices(current_price)
            
            # Send summary email
            self.alert_system.send_daily_summary(
                current_price,
                predictions,
                state_prices
            )
            
            logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}", exc_info=True)


def main():
    """Main scheduler loop"""
    logger.info("="*60)
    logger.info("Gold Price Monitoring System Started")
    logger.info("="*60)
    
    # Initialize monitor
    try:
        monitor = GoldPriceMonitor()
    except Exception as e:
        logger.error(f"Failed to initialize monitor: {e}")
        return
    
    # Schedule tasks
    
    # Check prices every hour (during market hours)
    schedule.every().hour.do(monitor.check_prices)
    
    # Send daily summary at 9:00 AM
    schedule.every().day.at("09:00").do(monitor.send_daily_summary)
    
    # Run initial check
    logger.info("Running initial price check...")
    monitor.check_prices()
    
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    logger.info("Tasks scheduled:")
    logger.info("  - Price check: Every hour")
    logger.info("  - Daily summary: 09:00 AM")
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    # You can customize the schedule here
    
    # Examples:
    # schedule.every(30).minutes.do(monitor.check_prices)  # Every 30 minutes
    # schedule.every().day.at("18:00").do(monitor.send_daily_summary)  # 6 PM
    # schedule.every().monday.at("09:00").do(monitor.send_weekly_summary)  # Monday 9 AM
    
    main()
