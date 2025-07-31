#!/usr/bin/env python3
"""
Fix admin account password
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Fix admin account password"""
    with app.app_context():
        # Get admin account
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("❌ No admin account found!")
            return False
        
        print(f"✅ Found admin account: {admin.team_name}")
        
        # Update password
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        
        print("✅ Admin password updated!")
        print("   Username: Admin")
        print("   Password: admin123")
        
        return True

if __name__ == '__main__':
    print("🔧 Fixing admin password...")
    fix_admin_password() 