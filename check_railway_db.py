#!/usr/bin/env python3
"""
Script to check Railway database connection and debug login issues
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import check_password_hash

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def check_railway_database():
    """Check Railway database connection and admin account"""
    
    with app.app_context():
        print("🔍 Checking Railway Database Connection...")
        
        # Check database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"📊 Database URI: {db_uri}")
        
        # Check if DATABASE_URL environment variable is set
        database_url = os.getenv('DATABASE_URL')
        print(f"🌐 DATABASE_URL env var: {database_url}")
        
        try:
            # Try to connect to database
            print("🔧 Testing database connection...")
            db.engine.connect()
            print("✅ Database connection successful!")
            
            # Check if tables exist
            print("📋 Checking tables...")
            tables = db.engine.table_names()
            print(f"📊 Found tables: {tables}")
            
            # Check user table
            if 'user' in tables:
                print("✅ User table exists!")
                
                # Count users
                user_count = User.query.count()
                print(f"👥 Total users: {user_count}")
                
                # Check admin accounts
                admin_users = User.query.filter_by(is_admin=True).all()
                print(f"👑 Admin users: {len(admin_users)}")
                
                for admin in admin_users:
                    print(f"   - {admin.team_name} (Status: {admin.status}, Is Admin: {admin.is_admin})")
                    
                    # Test password
                    password_valid = check_password_hash(admin.password_hash, "admin")
                    print(f"     Password 'admin' valid: {password_valid}")
                    
                    # Test with superadmin
                    if admin.team_name == "superadmin":
                        password_valid = check_password_hash(admin.password_hash, "admin")
                        print(f"     superadmin password valid: {password_valid}")
                
                # Try to find superadmin specifically
                superadmin = User.query.filter_by(team_name="superadmin").first()
                if superadmin:
                    print(f"\n🎯 Found superadmin account:")
                    print(f"   Team Name: {superadmin.team_name}")
                    print(f"   Status: {superadmin.status}")
                    print(f"   Is Admin: {superadmin.is_admin}")
                    
                    # Test password
                    password_valid = check_password_hash(superadmin.password_hash, "admin")
                    print(f"   Password 'admin' valid: {password_valid}")
                    
                    if password_valid:
                        print("✅ LOGIN SHOULD WORK!")
                        print("   Team Name: superadmin")
                        print("   Password: admin")
                    else:
                        print("❌ Password validation failed!")
                else:
                    print("❌ superadmin account not found!")
                    
            else:
                print("❌ User table does not exist!")
                
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("This means Railway is not using the PostgreSQL database!")

if __name__ == "__main__":
    print("🚀 Checking Railway Database...")
    check_railway_database()
    print("✅ Done!") 