#!/usr/bin/env python3
"""
Script to fix admin password hash for proper login
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def fix_admin_password():
    """Fix admin password hash to ensure login works"""
    
    with app.app_context():
        # Find admin account
        admin_user = User.query.filter_by(team_name="Admin").first()
        
        if not admin_user:
            print("❌ Admin account not found!")
            return
        
        # Update password hash
        admin_user.password_hash = generate_password_hash("admin123")
        admin_user.status = "active"
        
        try:
            db.session.commit()
            
            # Test the password
            if check_password_hash(admin_user.password_hash, "admin123"):
                print("✅ Admin password fixed successfully!")
                print(f"   Team Name: {admin_user.team_name}")
                print(f"   Password: admin123")
                print(f"   Status: {admin_user.status}")
                print(f"   Is Admin: {admin_user.is_admin}")
                print("\n🔐 You can now login with:")
                print("   Team Name: Admin")
                print("   Password: admin123")
            else:
                print("❌ Password hash test failed!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing admin password: {e}")

if __name__ == "__main__":
    print("🔧 Fixing admin password...")
    fix_admin_password()
    print("✅ Done!") 