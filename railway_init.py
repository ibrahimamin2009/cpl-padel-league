#!/usr/bin/env python3
"""
Script to initialize Railway database and add admin account
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def init_railway_db():
    """Initialize Railway database and add admin account"""
    
    with app.app_context():
        print("🔧 Initializing Railway database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created!")
        
        # Check if admin exists
        existing_admin = User.query.filter_by(team_name="superadmin").first()
        
        if existing_admin:
            print("✅ Admin account already exists!")
            print(f"   Team Name: {existing_admin.team_name}")
            print(f"   Status: {existing_admin.status}")
            print(f"   Is Admin: {existing_admin.is_admin}")
        else:
            # Create admin account
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
                print("✅ Admin account created!")
                print(f"   Team Name: superadmin")
                print(f"   Password: admin")
                print(f"   Status: active")
                print(f"   Is Admin: True")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin: {e}")
        
        # Verify admin account
        admin = User.query.filter_by(team_name="superadmin").first()
        if admin:
            print("\n🎉 LOGIN CREDENTIALS:")
            print("   Team Name: superadmin")
            print("   Password: admin")
            print("   ✅ Ready to login!")
        else:
            print("\n❌ Admin account not found!")

if __name__ == "__main__":
    print("🚀 Initializing Railway Database...")
    init_railway_db()
    print("✅ Done!") 