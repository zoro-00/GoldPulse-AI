"""
Email Alert System for Gold Price Prediction
Sends email notifications when thresholds are crossed
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from config import EMAIL_CONFIG, ALERT_THRESHOLDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailAlertSystem:
    """Email notification system for price alerts"""
    
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.sender_email = EMAIL_CONFIG['sender_email']
        self.sender_password = EMAIL_CONFIG['sender_password']
        self.recipients = EMAIL_CONFIG['recipient_emails']
        self.thresholds = ALERT_THRESHOLDS
        
        # Track last alert time to avoid spam
        self.last_alert = {}
        self.min_alert_interval = 3600  # 1 hour between similar alerts
    
    def should_send_alert(self, alert_type):
        """Check if enough time has passed since last alert of this type"""
        now = datetime.now()
        
        if alert_type not in self.last_alert:
            return True
        
        time_since_last = (now - self.last_alert[alert_type]).total_seconds()
        return time_since_last >= self.min_alert_interval
    
    def send_email(self, subject, body_html):
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            
            # Add HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def check_and_alert(self, current_price, predicted_price, previous_price=None):
        """Check thresholds and send alerts if necessary"""
        alerts_sent = []
        
        # Alert 1: Price crosses upper threshold
        if current_price > self.thresholds['price_upper_limit']:
            alert_type = 'price_high'
            if self.should_send_alert(alert_type):
                self.send_price_high_alert(current_price, predicted_price)
                self.last_alert[alert_type] = datetime.now()
                alerts_sent.append(alert_type)
        
        # Alert 2: Price crosses lower threshold
        if current_price < self.thresholds['price_lower_limit']:
            alert_type = 'price_low'
            if self.should_send_alert(alert_type):
                self.send_price_low_alert(current_price, predicted_price)
                self.last_alert[alert_type] = datetime.now()
                alerts_sent.append(alert_type)
        
        # Alert 3: Significant price change
        if previous_price:
            change_percent = abs((current_price - previous_price) / previous_price * 100)
            if change_percent >= self.thresholds['price_change_percent']:
                alert_type = 'price_change'
                if self.should_send_alert(alert_type):
                    direction = 'increased' if current_price > previous_price else 'decreased'
                    self.send_price_change_alert(
                        current_price, 
                        previous_price, 
                        change_percent, 
                        direction,
                        predicted_price
                    )
                    self.last_alert[alert_type] = datetime.now()
                    alerts_sent.append(alert_type)
        
        return alerts_sent
    
    def send_price_high_alert(self, current_price, predicted_price):
        """Send alert when price exceeds upper threshold"""
        subject = f"🚨 Gold Price Alert: High Threshold Crossed"
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">⚠️ High Price Alert</h2>
            <p>Gold price has exceeded the upper threshold!</p>
            
            <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p><strong>Current Price:</strong> ₹{current_price:,.2f} per 10g</p>
              <p><strong>Threshold:</strong> ₹{self.thresholds['price_upper_limit']:,.2f} per 10g</p>
              <p><strong>Predicted Price (Tomorrow):</strong> ₹{predicted_price:,.2f} per 10g</p>
            </div>
            
            <p style="color: #666;">
              <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            
            <p style="margin-top: 30px; color: #999; font-size: 12px;">
              This is an automated alert from Gold Price Prediction System
            </p>
          </body>
        </html>
        """
        
        self.send_email(subject, body)
    
    def send_price_low_alert(self, current_price, predicted_price):
        """Send alert when price falls below lower threshold"""
        subject = f"📉 Gold Price Alert: Low Threshold Crossed"
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #1976d2;">💡 Low Price Alert</h2>
            <p>Gold price has fallen below the lower threshold!</p>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p><strong>Current Price:</strong> ₹{current_price:,.2f} per 10g</p>
              <p><strong>Threshold:</strong> ₹{self.thresholds['price_lower_limit']:,.2f} per 10g</p>
              <p><strong>Predicted Price (Tomorrow):</strong> ₹{predicted_price:,.2f} per 10g</p>
            </div>
            
            <p style="color: #666;">
              <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            
            <p style="margin-top: 30px; color: #999; font-size: 12px;">
              This is an automated alert from Gold Price Prediction System
            </p>
          </body>
        </html>
        """
        
        self.send_email(subject, body)
    
    def send_price_change_alert(self, current_price, previous_price, change_percent, direction, predicted_price):
        """Send alert for significant price changes"""
        subject = f"📊 Gold Price Alert: {change_percent:.1f}% {direction.capitalize()}"
        
        color = '#d32f2f' if direction == 'increased' else '#1976d2'
        bg_color = '#ffebee' if direction == 'increased' else '#e3f2fd'
        icon = '📈' if direction == 'increased' else '📉'
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {color};">{icon} Significant Price Movement</h2>
            <p>Gold price has {direction} by {change_percent:.2f}%</p>
            
            <div style="background-color: {bg_color}; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p><strong>Previous Price:</strong> ₹{previous_price:,.2f} per 10g</p>
              <p><strong>Current Price:</strong> ₹{current_price:,.2f} per 10g</p>
              <p><strong>Change:</strong> ₹{abs(current_price - previous_price):,.2f} ({change_percent:.2f}%)</p>
              <p><strong>Predicted Price (Tomorrow):</strong> ₹{predicted_price:,.2f} per 10g</p>
            </div>
            
            <p style="color: #666;">
              <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
            
            <p style="margin-top: 30px; color: #999; font-size: 12px;">
              This is an automated alert from Gold Price Prediction System
            </p>
          </body>
        </html>
        """
        
        self.send_email(subject, body)
    
    def send_daily_summary(self, current_price, predictions, state_prices):
        """Send daily summary report"""
        subject = f"📊 Daily Gold Price Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Top 5 and bottom 5 states by price
        sorted_states = sorted(state_prices.items(), key=lambda x: x[1])
        cheapest_5 = sorted_states[:5]
        costliest_5 = sorted_states[-5:][::-1]
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #1976d2;">📊 Daily Gold Price Summary</h2>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <h3>Current Price</h3>
              <p style="font-size: 24px; color: #1976d2; margin: 10px 0;">
                ₹{current_price:,.2f} per 10g
              </p>
            </div>
            
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <h3>Predictions</h3>
              <p><strong>10-Day Forecast:</strong> ₹{predictions.get('10day', 0):,.2f}</p>
              <p><strong>30-Day Forecast:</strong> ₹{predictions.get('30day', 0):,.2f}</p>
              <p><strong>90-Day Forecast:</strong> ₹{predictions.get('90day', 0):,.2f}</p>
            </div>
            
            <div style="margin: 20px 0;">
              <h3>Top 5 Costliest States</h3>
              <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #ffebee;">
                  <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">State</th>
                  <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Price (₹/10g)</th>
                </tr>
                {''.join([f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{state}</td><td style="padding: 8px; text-align: right; border: 1px solid #ddd;">₹{price:,.2f}</td></tr>' for state, price in costliest_5])}
              </table>
            </div>
            
            <div style="margin: 20px 0;">
              <h3>Top 5 Cheapest States</h3>
              <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #e3f2fd;">
                  <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">State</th>
                  <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Price (₹/10g)</th>
                </tr>
                {''.join([f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{state}</td><td style="padding: 8px; text-align: right; border: 1px solid #ddd;">₹{price:,.2f}</td></tr>' for state, price in cheapest_5])}
              </table>
            </div>
            
            <p style="margin-top: 30px; color: #999; font-size: 12px;">
              This is an automated report from Gold Price Prediction System
            </p>
          </body>
        </html>
        """
        
        self.send_email(subject, body)
    
    def test_connection(self):
        """Test email configuration"""
        subject = "🪙 Gold Price Prediction System - Test Email"
        body = """
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2>✅ Email Alert System Test</h2>
            <p>This is a test email from your Gold Price Prediction System.</p>
            <p>If you're receiving this, your email configuration is working correctly!</p>
            <p style="margin-top: 20px; color: #999; font-size: 12px;">
              Timestamp: {timestamp}
            </p>
          </body>
        </html>
        """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return self.send_email(subject, body)


if __name__ == "__main__":
    # Test the email system
    print("Testing email alert system...")
    print("\n⚠️  Make sure to configure EMAIL_CONFIG in config.py first!")
    print("You need to set your email and app-specific password.")
    
    # Uncomment to test:
    # alert_system = EmailAlertSystem()
    # alert_system.test_connection()
