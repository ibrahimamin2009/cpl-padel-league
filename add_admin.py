#!/usr/bin/env python3
"""
Script to add an admin account with the specified email
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

def add_admin_account():
    """Add admin account with the specified email"""
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(team_name="Admin").first()
        
        if existing_admin:
            print(f"❌ Admin account with team name 'Admin' already exists!")
            print(f"   Team Name: {existing_admin.team_name}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            return
        
        # Create new admin account
        admin_user = User(
            team_name="Admin",
            player1_name="Admin User",
            player1_email="ibrahimamin9621@gmail.com",
            player2_name="Admin User",
            player2_email="ibrahimamin9621@gmail.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
            rank=0,
            tier="Admin",
            status="active",
            created_at=datetime.now(LAHORE_TZ)
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin account created successfully!")
            print(f"   Team Name: Admin")
            print(f"   Password: admin123")
            print(f"   Email: ibrahimamin9621@gmail.com")
            print(f"   Is Admin: {admin_user.is_admin}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin account: {e}")

if __name__ == "__main__":
    print("🔧 Adding admin account...")
    add_admin_account()
    print("✅ Done!") 