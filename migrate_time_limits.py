#!/usr/bin/env python3
"""
Database migration script to add time limit fields to existing CPL database.
This script adds the new deadline fields to the Match table and updates existing records.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os

# Set timezone to Lahore, Pakistan
LAHORE_TZ = ZoneInfo('Asia/Karachi')

def migrate_database():
    """Migrate the database to add time limit fields"""
    
    # Check if database exists
    if not os.path.exists('instance/cpl.db'):
        print("Database not found. Please run the application first to create the database.")
        return
    
    # Connect to database
    conn = sqlite3.connect('instance/cpl.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(match)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'match_deadline' not in columns:
            print("Adding match_deadline column...")
            cursor.execute("ALTER TABLE match ADD COLUMN match_deadline DATETIME")
        
        if 'score_deadline' not in columns:
            print("Adding score_deadline column...")
            cursor.execute("ALTER TABLE match ADD COLUMN score_deadline DATETIME")
        
        # Update existing matches with deadlines
        print("Updating existing matches with deadlines...")
        
        # Get all scheduled matches without deadlines
        cursor.execute("""
            SELECT id, created_at, status 
            FROM match 
            WHERE status = 'scheduled' AND match_deadline IS NULL
        """)
        
        scheduled_matches = cursor.fetchall()
        for match_id, created_at, status in scheduled_matches:
            if created_at:
                # Parse the created_at datetime
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    # Set deadline to 10 days from creation
                    deadline = created_dt.replace(tzinfo=LAHORE_TZ) + timedelta(days=10)
                    cursor.execute(
                        "UPDATE match SET match_deadline = ? WHERE id = ?",
                        (deadline.isoformat(), match_id)
                    )
                except ValueError:
                    print(f"Could not parse datetime for match {match_id}")
        
        # Get all played matches without score deadlines
        cursor.execute("""
            SELECT id, created_at, status 
            FROM match 
            WHERE status = 'played' AND score_deadline IS NULL
        """)
        
        played_matches = cursor.fetchall()
        for match_id, created_at, status in played_matches:
            if created_at:
                # Parse the created_at datetime
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    # Set score deadline to 5 hours from creation (or now if already overdue)
                    now = datetime.now(LAHORE_TZ)
                    deadline = created_dt.replace(tzinfo=LAHORE_TZ) + timedelta(hours=5)
                    if deadline < now:
                        deadline = now + timedelta(hours=1)  # Give 1 hour from now
                    cursor.execute(
                        "UPDATE match SET score_deadline = ? WHERE id = ?",
                        (deadline.isoformat(), match_id)
                    )
                except ValueError:
                    print(f"Could not parse datetime for match {match_id}")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM match WHERE match_deadline IS NOT NULL")
        match_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM match WHERE score_deadline IS NOT NULL")
        score_count = cursor.fetchone()[0]
        
        print(f"Updated {match_count} matches with match deadlines")
        print(f"Updated {score_count} matches with score deadlines")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting CPL database migration for time limits...")
    migrate_database()
    print("Migration script completed.") 