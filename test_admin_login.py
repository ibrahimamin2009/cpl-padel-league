#!/usr/bin/env python3
"""
Script to test admin login and debug the issue
"""

import os
import sys
from zoneinfo import ZoneInfo

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def test_admin_login():
    """Test admin login and debug the issue"""
    
    with app.app_context():
        # Find admin account
        admin_user = User.query.filter_by(team_name="Admin").first()
        
        if not admin_user:
            print("❌ Admin account not found!")
            return
        
        print("🔍 Admin Account Details:")
        print(f"   Team Name: {admin_user.team_name}")
        print(f"   Password Hash: {admin_user.password_hash}")
        print(f"   Status: {admin_user.status}")
        print(f"   Is Admin: {admin_user.is_admin}")
        
        # Test password
        test_password = "admin123"
        is_valid = check_password_hash(admin_user.password_hash, test_password)
        
        print(f"\n🔐 Password Test:")
        print(f"   Testing password: '{test_password}'")
        print(f"   Is valid: {is_valid}")
        
        if not is_valid:
            print("\n🔧 Fixing password hash...")
            admin_user.password_hash = generate_password_hash("admin123")
            admin_user.status = "active"
            
            try:
                db.session.commit()
                print("✅ Password hash updated!")
                
                # Test again
                is_valid = check_password_hash(admin_user.password_hash, test_password)
                print(f"   New test result: {is_valid}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error updating password: {e}")
        
        print(f"\n📝 Login Credentials:")
        print(f"   Team Name: Admin")
        print(f"   Password: admin123")

if __name__ == "__main__":
    print("🔧 Testing admin login...")
    test_admin_login()
    print("✅ Done!") 