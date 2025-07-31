#!/usr/bin/env python3
"""
Script to fix Railway database schema and ensure deployment works
"""

import os
import sys
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo

# Railway PostgreSQL connection details
DATABASE_URL = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def fix_railway_schema():
    """Fix Railway database schema"""
    
    try:
        # Connect to Railway PostgreSQL
        print("🔧 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database!")
        
        # Drop all tables to start fresh
        print("🧹 Dropping all tables...")
        cursor.execute("DROP TABLE IF EXISTS match CASCADE")
        cursor.execute("DROP TABLE IF EXISTS challenge CASCADE")
        cursor.execute("DROP TABLE IF EXISTS tier_config CASCADE")
        cursor.execute("DROP TABLE IF EXISTS \"user\" CASCADE")
        
        conn.commit()
        print("✅ All tables dropped!")
        
        # Create user table with correct schema
        print("📋 Creating user table...")
        cursor.execute("""
            CREATE TABLE "user" (
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
            CREATE TABLE challenge (
                id SERIAL PRIMARY KEY,
                challenging_team_id INTEGER REFERENCES "user"(id),
                challenged_team_id INTEGER REFERENCES "user"(id),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                match_id INTEGER
            )
        """)
        
        # Create match table with all required columns
        print("📋 Creating match table...")
        cursor.execute("""
            CREATE TABLE match (
                id SERIAL PRIMARY KEY,
                team1_id INTEGER REFERENCES "user"(id),
                team2_id INTEGER REFERENCES "user"(id),
                date TIMESTAMP,
                venue VARCHAR(200),
                status VARCHAR(20) DEFAULT 'scheduled',
                winner_id INTEGER REFERENCES "user"(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                match_deadline TIMESTAMP,
                score_deadline TIMESTAMP,
                set1_team1_score INTEGER,
                set1_team2_score INTEGER,
                set2_team1_score INTEGER,
                set2_team2_score INTEGER,
                set3_team1_score INTEGER,
                set3_team2_score INTEGER,
                proposed_date TIMESTAMP,
                proposed_venue VARCHAR(200),
                proposed_by INTEGER REFERENCES "user"(id),
                venue_approved BOOLEAN,
                venue_approved_by INTEGER REFERENCES "user"(id),
                score_entered_by INTEGER REFERENCES "user"(id),
                score_approved BOOLEAN,
                score_approved_by INTEGER REFERENCES "user"(id),
                score_disputed BOOLEAN DEFAULT FALSE,
                score_dispute_reason VARCHAR(500)
            )
        """)
        
        # Create tier_config table with correct schema
        print("📋 Creating tier_config table...")
        cursor.execute("""
            CREATE TABLE tier_config (
                id SERIAL PRIMARY KEY,
                tier_name VARCHAR(50) UNIQUE NOT NULL,
                max_rank INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ All tables created with correct schema!")
        
        # Create admin account
        print("👤 Creating admin account...")
        from werkzeug.security import generate_password_hash
        admin_password_hash = generate_password_hash("admin")
        current_time = datetime.now(LAHORE_TZ)
        
        cursor.execute("""
            INSERT INTO "user" (team_name, player1_name, player1_email, player2_name, player2_email, 
                              password_hash, tier, rank, status, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            "admin",
            "Admin",
            "admin@cpl.com",
            "Admin", 
            "admin@cpl.com",
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
        cursor.execute("SELECT team_name, is_admin, status FROM \"user\" WHERE team_name = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print("\n🎉 FRESH ADMIN ACCOUNT READY!")
            print("   Team Name: admin")
            print("   Password: admin")
            print("   Status: active")
            print("   Is Admin: True")
            print("   ✅ Ready to login!")
        else:
            print("\n❌ Admin account not found!")
        
        cursor.close()
        conn.close()
        print("✅ Database schema fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Fixing Railway Database Schema...")
    fix_railway_schema()
    print("✅ Done!") 