#!/usr/bin/env python3
"""
Script to test Railway deployment startup
"""

import os
import sys

# Force Railway environment
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ['DATABASE_URL'] = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"

def test_railway_startup():
    """Test Railway deployment startup"""
    
    print("🚀 Testing Railway deployment startup...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from app import app, db
        print("✅ App imports successful!")
        
        # Test database connection
        print("🔧 Testing database connection...")
        with app.app_context():
            db.engine.connect()
            print("✅ Database connection successful!")
            
            # Test table creation
            print("📋 Testing table creation...")
            db.create_all()
            print("✅ Table creation successful!")
            
            # Test basic query
            print("🔍 Testing basic query...")
            from app import User
            user_count = User.query.count()
            print(f"✅ Basic query successful! User count: {user_count}")
            
        print("\n🎉 Railway deployment test PASSED!")
        print("✅ All components working correctly!")
        
    except Exception as e:
        print(f"❌ Railway deployment test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_railway_startup() 