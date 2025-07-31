#!/usr/bin/env python3
"""
CPL Deployment Script
Helps set up the database and create initial admin user
"""

import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user for the application"""
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
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            rank=0,
            tier='Admin'
        )
        
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print("   Username: Admin")
        print("   Password: admin123")
        return admin

def setup_database():
    """Set up the database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
        
        # Initialize default tiers
        from app import initialize_default_tiers
        initialize_default_tiers()
        print("✅ Default tiers initialized!")

def main():
    """Main deployment function"""
    print("🚀 CPL Deployment Script")
    print("=" * 40)
    
    # Set up database
    setup_database()
    
    # Create admin user
    create_admin_user()
    
    print("\n✅ Deployment complete!")
    print("\n📋 Next steps:")
    print("1. Deploy to Railway/Render/PythonAnywhere")
    print("2. Set environment variables:")
    print("   - SECRET_KEY")
    print("   - DATABASE_URL (if using external DB)")
    print("3. Access your app and login as Admin")
    print("4. Create teams and start your league!")

if __name__ == '__main__':
    main() 