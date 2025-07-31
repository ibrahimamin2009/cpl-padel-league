#!/usr/bin/env python3
"""
Script to directly initialize Railway PostgreSQL database
"""

import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash

# Railway PostgreSQL connection details
DATABASE_URL = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def init_railway_database():
    """Initialize Railway PostgreSQL database directly"""
    
    try:
        # Connect to Railway PostgreSQL
        print("🔧 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database!")
        
        # Create user table
        print("📋 Creating user table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) UNIQUE NOT NULL,
                player1_name VARCHAR(100) NOT NULL,
                player1_email VARCHAR(100) NOT NULL,
                player2_name VARCHAR(100) NOT NULL,
                player2_email VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                tier VARCHAR(50) DEFAULT 'Bronze',
                rank INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                forfeit_count INTEGER DEFAULT 0,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create challenge table
        print("📋 Creating challenge table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenge (
                id SERIAL PRIMARY KEY,
                challenger_id INTEGER REFERENCES "user"(id),
                challenged_id INTEGER REFERENCES "user"(id),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # Create match table
        print("📋 Creating match table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match (
                id SERIAL PRIMARY KEY,
                challenge_id INTEGER REFERENCES challenge(id),
                team1_id INTEGER REFERENCES "user"(id),
                team2_id INTEGER REFERENCES "user"(id),
                team1_score INTEGER,
                team2_score INTEGER,
                venue VARCHAR(200),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score_deadline TIMESTAMP,
                score_approved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create tier_config table
        print("📋 Creating tier_config table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tier_config (
                id SERIAL PRIMARY KEY,
                tier_name VARCHAR(50) UNIQUE NOT NULL,
                min_rank INTEGER NOT NULL,
                max_rank INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ All tables created successfully!")
        
        # Check if admin exists
        cursor.execute("SELECT team_name, is_admin, status FROM \"user\" WHERE is_admin = TRUE")
        existing_admins = cursor.fetchall()
        
        if existing_admins:
            print("✅ Admin accounts found:")
            for admin in existing_admins:
                print(f"   - {admin[0]} (Admin: {admin[1]}, Status: {admin[2]})")
        else:
            # Create admin account
            print("👤 Creating admin account...")
            admin_password_hash = generate_password_hash("admin")
            current_time = datetime.now(LAHORE_TZ)
            
            cursor.execute("""
                INSERT INTO "user" (team_name, player1_name, player1_email, player2_name, player2_email, 
                                  password_hash, tier, rank, status, is_admin, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                "superadmin",
                "Admin",
                "admin@test.com",
                "Admin", 
                "admin@test.com",
                admin_password_hash,
                "Admin",
                0,
                "active",
                True,
                current_time
            ))
            
            conn.commit()
            print("✅ Admin account created!")
        
        # Verify admin account
        cursor.execute("SELECT team_name, is_admin, status FROM \"user\" WHERE team_name = 'superadmin'")
        admin = cursor.fetchone()
        
        if admin:
            print("\n🎉 LOGIN CREDENTIALS:")
            print("   Team Name: superadmin")
            print("   Password: admin")
            print("   Status: active")
            print("   Is Admin: True")
            print("   ✅ Ready to login!")
        else:
            print("\n❌ Admin account not found!")
        
        cursor.close()
        conn.close()
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Initializing Railway PostgreSQL Database...")
    init_railway_database()
    print("✅ Done!") 