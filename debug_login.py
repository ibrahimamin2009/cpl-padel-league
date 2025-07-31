#!/usr/bin/env python3
"""
Script to debug login issues and create a working admin account
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

def debug_login():
    """Debug login issues and create working admin"""
    
    with app.app_context():
        # Delete any existing admin accounts
        existing_admins = User.query.filter_by(is_admin=True).all()
        for admin in existing_admins:
            print(f"Deleting existing admin: {admin.team_name}")
            db.session.delete(admin)
        
        # Create a completely new admin account
        admin_user = User(
            team_name="superadmin",
            player1_name="Admin",
            player1_email="admin@test.com",
            player2_name="Admin",
            player2_email="admin@test.com",
            password_hash=generate_password_hash("admin"),
            is_admin=True,
            rank=0,
            tier="Admin",
            status="active",
            created_at=datetime.now(LAHORE_TZ)
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            # Test the account
            test_user = User.query.filter_by(team_name="superadmin").first()
            if test_user:
                password_valid = check_password_hash(test_user.password_hash, "admin")
                
                print("✅ Admin account created and tested!")
                print(f"   Team Name: {test_user.team_name}")
                print(f"   Password: admin")
                print(f"   Status: {test_user.status}")
                print(f"   Is Admin: {test_user.is_admin}")
                print(f"   Password Valid: {password_valid}")
                
                if password_valid:
                    print("\n🎉 LOGIN SHOULD WORK NOW!")
                    print("   Team Name: superadmin")
                    print("   Password: admin")
                else:
                    print("\n❌ Password validation failed!")
            else:
                print("❌ Admin account not found after creation!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Debugging login and creating fresh admin...")
    debug_login()
    print("✅ Done!") 