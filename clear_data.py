#!/usr/bin/env python3
"""
Clear all data except admin account for deployment
"""
import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Challenge, Match, TierConfig, LAHORE_TZ

def clear_all_data_except_admin():
    """Clear all data except admin account"""
    with app.app_context():
        print("🗑️  Clearing all data except admin account...")
        
        # Get admin account
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ No admin account found!")
            return False
        
        print(f"✅ Found admin account: {admin.team_name}")
        
        # Delete all challenges
        challenges_count = Challenge.query.count()
        Challenge.query.delete()
        print(f"🗑️  Deleted {challenges_count} challenges")
        
        # Delete all matches
        matches_count = Match.query.count()
        Match.query.delete()
        print(f"🗑️  Deleted {matches_count} matches")
        
        # Delete all non-admin users
        non_admin_users = User.query.filter_by(is_admin=False).all()
        non_admin_count = len(non_admin_users)
        for user in non_admin_users:
            db.session.delete(user)
        print(f"🗑️  Deleted {non_admin_count} non-admin users")
        
        # Reset admin account to default values
        admin.team_name = "Admin"
        admin.player1_name = "Admin"
        admin.player1_email = "admin@cpl.com"
        admin.player2_name = "Admin"
        admin.player2_email = "admin@cpl.com"
        admin.rank = 0
        admin.tier = "Admin"
        admin.forfeit_count = 0
        admin.status = "active"
        admin.created_at = datetime.now(LAHORE_TZ)
        
        # Reset tier configurations to defaults
        TierConfig.query.delete()
        print("🗑️  Reset tier configurations")
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database cleared successfully!")
        print(f"✅ Admin account preserved: {admin.team_name}")
        
        # Verify cleanup
        remaining_users = User.query.count()
        remaining_challenges = Challenge.query.count()
        remaining_matches = Match.query.count()
        
        print(f"\n📊 Database Status:")
        print(f"   Users: {remaining_users} (should be 1)")
        print(f"   Challenges: {remaining_challenges} (should be 0)")
        print(f"   Matches: {remaining_matches} (should be 0)")
        
        if remaining_users == 1 and remaining_challenges == 0 and remaining_matches == 0:
            print("✅ Cleanup successful!")
            return True
        else:
            print("❌ Cleanup incomplete!")
            return False

if __name__ == "__main__":
    print("🧹 CPL Database Cleanup Tool")
    print("=" * 40)
    
    response = input("⚠️  This will delete ALL teams, challenges, and matches except admin. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = clear_all_data_except_admin()
        if success:
            print("\n🎉 Database ready for deployment!")
            print("📝 Admin login:")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("\n❌ Cleanup failed!")
            sys.exit(1)
    else:
        print("❌ Operation cancelled.")
        sys.exit(0) 