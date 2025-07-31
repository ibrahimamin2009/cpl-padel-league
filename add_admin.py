#!/usr/bin/env python3
"""
Add Admin User to Railway Database
Run this script to create the admin user in your Railway database
"""

import os
from app import app, db, User
from werkzeug.security import generate_password_hash

def add_admin_user():
    """Add admin user to the database"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            print(f"✅ Admin user already exists: {admin.team_name}")
            return admin
        
        # Create admin user
        admin = User(
            team_name='Admin',
            player1_name='Administrator',
            player1_email='admin@cpl.com',
            player2_name='Admin',
            player2_email='admin@cpl.com',
            password_hash='admin123',  # Simple password for now
            is_admin=True,
            rank=0,
            tier='Admin',
            status='active'
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print("   Username: Admin")
        print("   Password: admin123")
        return admin

if __name__ == '__main__':
    print("🚀 Adding Admin User to Railway Database")
    print("=" * 50)
    add_admin_user()
    print("\n✅ Done! You can now login as Admin with password: admin123") 