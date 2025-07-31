#!/usr/bin/env python3
"""
Script to clear all data from the Chiniot Padel League database and remove admin account.
This will reset the database to a clean state.
"""

import os
import sys
from app import app, db, User, Challenge, Match

def clear_all_data():
    """Clear all data from the database"""
    with app.app_context():
        print("Clearing all data from the database...")
        
        # Delete all matches
        matches_deleted = Match.query.delete()
        print(f"Deleted {matches_deleted} matches")
        
        # Delete all challenges
        challenges_deleted = Challenge.query.delete()
        print(f"Deleted {challenges_deleted} challenges")
        
        # Delete all users (including admin)
        users_deleted = User.query.delete()
        print(f"Deleted {users_deleted} users (including admin account)")
        
        # Commit the changes
        db.session.commit()
        
        print("\n✅ Database cleared successfully!")
        print("All matches, challenges, and users have been removed.")
        print("The admin account has been deleted.")
        print("\nTo create a new admin account, register a new team and manually set is_admin=True in the database.")

if __name__ == '__main__':
    # Confirm before proceeding
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("This includes:")
    print("- All teams and users")
    print("- All matches")
    print("- All challenges")
    print("- The admin account")
    print("\nThis action cannot be undone!")
    
    response = input("\nAre you sure you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        clear_all_data()
    else:
        print("Operation cancelled.")
        sys.exit(0) 