#!/usr/bin/env python3
"""
Script to force Railway to use PostgreSQL database
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

def force_railway_postgres():
    """Force Railway to use PostgreSQL and create admin account"""
    
    with app.app_context():
        print("🔧 Forcing Railway to use PostgreSQL...")
        
        # Check database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"📊 Database URI: {db_uri}")
        
        try:
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
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Forcing Railway PostgreSQL...")
    force_railway_postgres()
    print("✅ Done!") 