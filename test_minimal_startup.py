#!/usr/bin/env python3
"""
Minimal test to identify Railway startup issues
"""

import os
import sys

def test_minimal_imports():
    """Test minimal imports without database"""
    
    print("🚀 Testing minimal imports...")
    
    try:
        # Test basic imports
        print("📦 Testing basic imports...")
        from flask import Flask
        print("✅ Flask import successful!")
        
        # Test app import without database
        print("📦 Testing app import...")
        from app import app
        print("✅ App import successful!")
        
        print("\n🎉 Minimal startup test PASSED!")
        print("✅ Basic imports working!")
        
    except Exception as e:
        print(f"❌ Minimal startup test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_imports() 