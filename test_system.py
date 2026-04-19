"""
Test Suite for Gold Price Prediction System
Run this to validate your setup
"""

import sys
import os


def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print('='*60)


def test_imports():
    """Test if all required packages can be imported"""
    print_test_header("Package Imports")
    
    packages = [
        'pandas',
        'numpy',
        'sklearn',
        'xgboost',
        'yfinance',
        'streamlit',
        'plotly',
        'smtplib',
        'schedule'
    ]
    
    failed = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully")
        return True


def test_config():
    """Test configuration file"""
    print_test_header("Configuration")
    
    try:
        from config import (
            EMAIL_CONFIG,
            ALERT_THRESHOLDS,
            DASHBOARD_CONFIG,
            DATA_CONFIG,
            STATE_FACTORS,
            MODEL_PATHS
        )
        
        print("✅ config.py loaded")
        print(f"   States configured: {len(STATE_FACTORS)}")
        print(f"   Alert thresholds: {len(ALERT_THRESHOLDS)}")
        print(f"   Data sources: {len(DATA_CONFIG['tickers'])}")
        
        # Check if email is configured
        if EMAIL_CONFIG['sender_email'] == 'your_email@gmail.com':
            print("⚠️  Email not configured (using default)")
        else:
            print(f"✅ Email configured: {EMAIL_CONFIG['sender_email']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def test_data_pipeline():
    """Test data fetching"""
    print_test_header("Data Pipeline")
    
    try:
        from data_pipeline import GoldDataPipeline
        
        pipeline = GoldDataPipeline()
        print("✅ GoldDataPipeline initialized")
        
        # Test current price fetching
        print("\nFetching current price...")
        current = pipeline.get_current_price()
        
        if current:
            print(f"✅ Current price fetched:")
            print(f"   Gold (USD/oz): ${current['gold_usd_oz']:.2f}")
            print(f"   USD/INR: ₹{current['usd_inr']:.2f}")
            print(f"   Gold (INR/10g): ₹{current['gold_inr_10g']:.2f}")
        else:
            print("⚠️  Could not fetch current price")
            print("   This may be due to market hours or API limits")
        
        # Test state price calculation
        state_prices = pipeline.calculate_state_prices(60000)
        print(f"\n✅ State prices calculated ({len(state_prices)} states)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """Test if models exist and can be loaded"""
    print_test_header("Model Files")
    
    from config import MODEL_PATHS
    
    required_models = ['xgboost', 'feature_columns']
    optional_models = ['scaler']
    all_exist = True

    for model_name in required_models + optional_models:
        path = MODEL_PATHS.get(model_name)
        if path is None:
            if model_name in required_models:
                print(f"❌ {model_name}: path not configured")
                all_exist = False
            continue

        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {model_name}: {path} ({size:,} bytes)")
        else:
            if model_name in required_models:
                print(f"❌ {model_name}: {path} NOT FOUND")
                all_exist = False
            else:
                print(f"⚠️  {model_name}: {path} NOT FOUND (optional)")
    
    if not all_exist:
        print("\n⚠️  Models not found. You need to:")
        print("   1. Run your notebook completely")
        print("   2. Add the save_models code at the end")
        print("   3. Run that cell to create the model files")
        return False
    
    # Try to load models
    try:
        from model_inference import GoldPricePredictor
        
        predictor = GoldPricePredictor()
        success = predictor.load_models()
        
        if success:
            print("\n✅ Models loaded successfully")
            print(f"   Features: {len(predictor.feature_columns)}")
            return True
        else:
            print("\n❌ Failed to load models")
            return False
            
    except Exception as e:
        print(f"\n❌ Error loading models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_config():
    """Test email configuration"""
    print_test_header("Email System")
    
    try:
        from email_alerts import EmailAlertSystem
        from config import EMAIL_CONFIG
        
        alert_system = EmailAlertSystem()
        print("✅ EmailAlertSystem initialized")
        
        if EMAIL_CONFIG['sender_email'] == 'your_email@gmail.com':
            print("⚠️  Email not configured")
            print("   Edit config.py to set up email alerts")
            return True  # Not an error, just not configured
        else:
            print(f"✅ Email configured for: {EMAIL_CONFIG['sender_email']}")
            print(f"   Recipients: {len(EMAIL_CONFIG['recipient_emails'])}")
            
            # Ask if user wants to test
            test = input("\nSend test email? (y/N): ").strip().lower()
            if test == 'y':
                if alert_system.test_connection():
                    print("✅ Test email sent successfully!")
                else:
                    print("❌ Failed to send test email")
                    print("   Check your email configuration")
            
            return True
            
    except Exception as e:
        print(f"❌ Error with email system: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directories():
    """Test if required directories exist"""
    print_test_header("Directory Structure")
    
    required_dirs = ['models', 'logs']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"⚠️  {dir_name}/ not found, creating...")
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ Created {dir_name}/")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Gold Price Prediction System - Test Suite")
    print("="*60)
    
    results = {
        'Imports': test_imports(),
        'Directories': test_directories(),
        'Configuration': test_config(),
        'Data Pipeline': test_data_pipeline(),
        'Models': test_models(),
        'Email System': test_email_config(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready.")
        print("\nNext steps:")
        print("  1. Run the dashboard: streamlit run streamlit_dashboard.py")
        print("  2. Or start monitoring: python scheduler.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
