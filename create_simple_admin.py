#!/usr/bin/env python3
"""
Script to create a simple admin account
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

def create_simple_admin():
    """Create a simple admin account"""
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(team_name="admin").first()
        
        if existing_admin:
            print(f"❌ Admin account with team name 'admin' already exists!")
            print(f"   Team Name: {existing_admin.team_name}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            return
        
        # Create new admin account
        admin_user = User(
            team_name="admin",
            player1_name="Admin User",
            player1_email="admin@cpl.com",
            player2_name="Admin User",
            player2_email="admin@cpl.com",
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
            
            print("✅ Simple admin account created successfully!")
            print(f"   Team Name: admin")
            print(f"   Password: admin")
            print(f"   Email: admin@cpl.com")
            print(f"   Is Admin: {admin_user.is_admin}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin account: {e}")

if __name__ == "__main__":
    print("🔧 Creating simple admin account...")
    create_simple_admin()
    print("✅ Done!") 