#!/usr/bin/env python3
"""
Test script to demonstrate the tier system functionality.
This script shows how tiers are automatically assigned and updated.
"""

import os
import sys
from app import app, db, User, get_tier_for_rank, update_all_tiers

def test_tier_system():
    """Test the tier system functionality"""
    with app.app_context():
        print("🏆 Chiniot Padel League Tier System Test")
        print("=" * 50)
        
        # Test tier assignment for different ranks
        print("\n📊 Tier Assignment Rules:")
        print("- Ranks 1-10: Platinum")
        print("- Ranks 11-30: Gold") 
        print("- Ranks 31-60: Silver")
        print("- Ranks 61+: Bronze")
        
        print("\n🔍 Testing tier assignment for different ranks:")
        for rank in [1, 5, 10, 11, 20, 30, 31, 40, 50, 60, 61, 70, 80]:
            tier = get_tier_for_rank(rank)
            print(f"Rank {rank:2d} → {tier}")
        
        # Show current teams and their tiers
        print("\n👥 Current Teams and Tiers:")
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).all()
        
        if teams:
            print(f"{'Rank':<4} {'Team Name':<20} {'Tier':<10}")
            print("-" * 40)
            for team in teams:
                print(f"{team.rank:<4} {team.team_name:<20} {team.tier:<10}")
        else:
            print("No teams found in the database.")
        
        # Update all tiers
        print("\n🔄 Updating all team tiers...")
        update_all_tiers()
        
        # Show updated teams
        print("\n✅ Updated Teams and Tiers:")
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).all()
        
        if teams:
            print(f"{'Rank':<4} {'Team Name':<20} {'Tier':<10}")
            print("-" * 40)
            for team in teams:
                print(f"{team.rank:<4} {team.team_name:<20} {team.tier:<10}")
        else:
            print("No teams found in the database.")
        
        print("\n🎯 Tier System Features:")
        print("✅ Automatic tier assignment based on rank")
        print("✅ Tiers update when teams move up/down ladder")
        print("✅ Tiers update when admin changes team ranks")
        print("✅ Tiers update when new teams register")
        print("✅ Tiers are calculated on application startup")

if __name__ == '__main__':
    test_tier_system() 