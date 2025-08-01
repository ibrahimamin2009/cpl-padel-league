#!/usr/bin/env python3
"""
Test Railway deployment environment
"""

import os
import sys

def test_railway_env():
    """Test Railway environment variables and imports"""
    
    print("🚀 Testing Railway deployment environment...")
    
    # Check environment variables
    print("📊 Environment Variables:")
    print(f"   PORT: {os.getenv('PORT', 'Not set')}")
    print(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"   PYTHON_VERSION: {os.getenv('PYTHON_VERSION', 'Not set')}")
    
    # Test basic imports
    try:
        print("\n📦 Testing Flask import...")
        from flask import Flask
        print("✅ Flask import successful!")
        
        print("📦 Testing gunicorn import...")
        import gunicorn
        print("✅ Gunicorn import successful!")
        
        print("\n🎉 Railway environment test PASSED!")
        print("✅ All imports working!")
        
    except Exception as e:
        print(f"❌ Railway environment test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_railway_env() 