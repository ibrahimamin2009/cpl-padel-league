#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""
import os
import sys

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        print("✅ datetime and ZoneInfo imports successful")
        
        # Test Flask imports
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_mail import Mail, Message
        print("✅ Flask imports successful")
        
        # Test app import
        from app import app, db, User, Challenge, Match, LAHORE_TZ
        print("✅ App imports successful")
        
        # Test timezone
        now = datetime.now(LAHORE_TZ)
        print(f"✅ Timezone working: {now}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_context():
    """Test if app can start in context"""
    try:
        from app import app, db
        
        with app.app_context():
            print("✅ App context created successfully")
            
            # Test database connection
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
            
        return True
        
    except Exception as e:
        print(f"❌ App context error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing deployment readiness...")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed!")
        return False
    
    # Test app context
    if not test_app_context():
        print("❌ App context tests failed!")
        return False
    
    print("=" * 40)
    print("✅ All tests passed! App is ready for deployment.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 