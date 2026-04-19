#!/usr/bin/env python3
"""
Setup script for Gold Price Prediction System
Automates initial configuration and setup
"""

import os
import sys
import subprocess


def print_banner():
    """Print setup banner"""
    print("="*60)
    print("🪙 Gold Price Prediction System - Setup")
    print("="*60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install required packages"""
    print("\nInstalling dependencies...")
    print("This may take a few minutes...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\nCreating project directories...")
    
    directories = ['models', 'logs']
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created {dir_name}/")
    
    return True


def check_models():
    """Check if models exist"""
    print("\nChecking for trained models...")
    
    model_files = [
        'models/xgboost_model.pkl',
        'models/feature_columns.pkl'
    ]
    
    all_exist = all(os.path.exists(f) for f in model_files)
    
    if all_exist:
        print("✅ All model files found")
        return True
    else:
        print("⚠️  Model files not found")
        print("\nTo create model files:")
        print("1. Open Gold_Price_Prediction_Phase1_XGBoost.ipynb")
        print("2. Run all cells to train the models")
        print("3. Or use the automated retraining script:")
        print()
        print("   python train_and_backtest_model.py")
        print()
        return False


def configure_email():
    """Interactive email configuration"""
    print("\nEmail Configuration (Optional)")
    print("Press Enter to skip email setup for now")
    print()
    
    setup_email = input("Do you want to configure email alerts now? (y/N): ").strip().lower()
    
    if setup_email == 'y':
        print("\nEmail Settings:")
        sender_email = input("Sender email address: ").strip()
        
        if sender_email:
            print("\n⚠️  For Gmail:")
            print("   1. Enable 2-Step Verification")
            print("   2. Generate App Password at https://myaccount.google.com/apppasswords")
            print("   3. Use the app password (not your regular password)")
            print()
            
            sender_password = input("App password (will not be echoed): ").strip()
            recipient_emails = input("Recipient emails (comma-separated): ").strip()
            
            # Update config.py
            try:
                with open('config.py', 'r') as f:
                    config_content = f.read()
                
                # Replace placeholder values
                config_content = config_content.replace(
                    "'sender_email': 'your_email@gmail.com'",
                    f"'sender_email': '{sender_email}'"
                )
                config_content = config_content.replace(
                    "'sender_password': 'your_app_password'",
                    f"'sender_password': '{sender_password}'"
                )
                
                if recipient_emails:
                    recipients = [f"'{email.strip()}'" for email in recipient_emails.split(',')]
                    recipients_str = f"[{', '.join(recipients)}]"
                    config_content = config_content.replace(
                        "'recipient_emails': [\n        'recipient1@example.com',\n        'recipient2@example.com'\n    ]",
                        f"'recipient_emails': {recipients_str}"
                    )
                
                with open('config.py', 'w') as f:
                    f.write(config_content)
                
                print("✅ Email configuration saved to config.py")
                
                # Test email
                test = input("\nSend test email now? (y/N): ").strip().lower()
                if test == 'y':
                    try:
                        from email_alerts import EmailAlertSystem
                        alert_system = EmailAlertSystem()
                        if alert_system.test_connection():
                            print("✅ Test email sent successfully!")
                        else:
                            print("❌ Failed to send test email. Check your settings.")
                    except Exception as e:
                        print(f"❌ Error testing email: {e}")
                
            except Exception as e:
                print(f"❌ Failed to update config: {e}")
                print("   Please manually edit config.py")
    else:
        print("⏭️  Skipped email configuration")
        print("   You can configure it later by editing config.py")


def test_data_pipeline():
    """Test data fetching"""
    print("\nTesting data pipeline...")
    
    try:
        from data_pipeline import GoldDataPipeline
        pipeline = GoldDataPipeline()
        
        current = pipeline.get_current_price()
        
        if current:
            print("✅ Data pipeline working")
            print(f"   Current gold price: ₹{current['gold_inr_10g']:,.2f}/10g")
            return True
        else:
            print("⚠️  Could not fetch current price")
            print("   Internet connection or Yahoo Finance API may be unavailable")
            return False
            
    except Exception as e:
        print(f"⚠️  Data pipeline test failed: {e}")
        return False


def print_next_steps(models_exist):
    """Print next steps"""
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    
    if not models_exist:
        print("\n📝 Next Steps:")
        print()
        print("1. Train your models:")
        print("   - Open Gold_Price_Prediction_Phase1_XGBoost.ipynb")
        print("   - Run all cells")
        print("   - Add the save_models code at the end (see README.md)")
        print()
        print("2. Run the dashboard:")
        print("   streamlit run streamlit_dashboard.py")
        print()
    else:
        print("\n🚀 You're all set! Run the dashboard:")
        print()
        print("   streamlit run streamlit_dashboard.py")
        print()
        print("Or start automated monitoring:")
        print()
        print("   python scheduler.py")
        print()
    
    print("📖 For detailed instructions, see README.md")
    print("="*60)


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup incomplete. Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check models
    models_exist = check_models()
    
    # Configure email
    configure_email()
    
    # Test data pipeline
    test_data_pipeline()
    
    # Print next steps
    print_next_steps(models_exist)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
