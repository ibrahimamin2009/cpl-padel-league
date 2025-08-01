#!/usr/bin/env python3
"""
Script to initialize Railway database and create admin account
"""
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Set Railway environment
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ['DATABASE_URL'] = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app_railway_fixed import app, db, User
from werkzeug.security import generate_password_hash

LAHORE_TZ = ZoneInfo('Asia/Karachi')

def init_railway_db():
    with app.app_context():
        print("🔧 Initializing Railway database...")
        
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created!")
            
            # Check if admin exists
            existing_admin = User.query.filter_by(team_name="admin").first()
            if existing_admin:
                print("✅ Admin account already exists!")
                print(f"   Team Name: {existing_admin.team_name}")
                print(f"   Status: {existing_admin.status}")
                print(f"   Is Admin: {existing_admin.is_admin}")
            else:
                # Create admin account
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
                
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin account created!")
                print(f"   Team Name: admin")
                print(f"   Password: admin")
                print(f"   Status: active")
                print(f"   Is Admin: True")
            
            # Verify admin account
            admin = User.query.filter_by(team_name="admin").first()
            if admin:
                print("\n🎉 LOGIN CREDENTIALS:")
                print("   Team Name: admin")
                print("   Password: admin")
                print("   ✅ Ready to login!")
            else:
                print("\n❌ Admin account not found!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Initializing Railway Database...")
    init_railway_db()
    print("✅ Done!") 