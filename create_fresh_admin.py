#!/usr/bin/env python3
"""
Script to create a brand new admin account with simple credentials
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force Railway environment
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ['DATABASE_URL'] = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"

from app import app, db, User
from werkzeug.security import generate_password_hash

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def create_fresh_admin():
    """Create a brand new admin account"""
    
    with app.app_context():
        print("🧹 Creating fresh admin account...")
        
        # Check database connection
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"📊 Database URI: {db_uri}")
        
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created!")
            
            # Create simple admin account
            admin_user = User(
                team_name="admin",
                player1_name="Admin",
                player1_email="admin@cpl.com",
                player2_name="Admin",
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
                print("✅ Fresh admin account created!")
                print(f"   Team Name: admin")
                print(f"   Password: admin")
                print(f"   Status: active")
                print(f"   Is Admin: True")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin: {e}")
                return
            
            # Verify admin account
            admin = User.query.filter_by(team_name="admin").first()
            if admin:
                print("\n🎉 FRESH ADMIN ACCOUNT READY!")
                print("   Team Name: admin")
                print("   Password: admin")
                print("   ✅ Ready to login!")
                
                # Test password
                from werkzeug.security import check_password_hash
                password_valid = check_password_hash(admin.password_hash, "admin")
                print(f"   Password test: {password_valid}")
                
            else:
                print("\n❌ Admin account not found!")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Creating Fresh Admin Account...")
    create_fresh_admin()
    print("✅ Done!") 