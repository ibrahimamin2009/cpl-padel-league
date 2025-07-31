#!/usr/bin/env python3
"""
Simple test to demonstrate the consecutive challenge rule.
"""

import os
import sys
from app import app, db, User, Challenge, Match, can_challenge
from datetime import datetime, timezone, timedelta

def simple_consecutive_test():
    """Simple test of the consecutive challenge rule"""
    with app.app_context():
        print("🏆 Simple Consecutive Challenge Rule Test")
        print("=" * 50)
        
        # Get teams
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).limit(10).all()
        
        if len(teams) < 4:
            print("❌ Need at least 4 teams")
            return
        
        print(f"\n👥 Teams:")
        for team in teams[:5]:
            print(f"   {team.rank}: {team.team_name} ({team.tier})")
        
        # Find a non-Platinum team and a target
        challenger = None
        target = None
        
        for team in teams:
            if team.tier != 'Platinum':
                challenger = team
                # Find a target they can challenge
                for t in teams:
                    if t.id != team.id:
                        rank_diff = team.rank - t.rank
                        if 1 <= rank_diff <= 3:
                            target = t
                            break
                if target:
                    break
        
        if not challenger or not target:
            print("❌ Could not find suitable teams")
            return
        
        print(f"\n🎯 Test Setup:")
        print(f"   Challenger: {challenger.team_name} (Rank {challenger.rank}, Tier {challenger.tier})")
        print(f"   Target: {target.team_name} (Rank {target.rank}, Tier {target.tier})")
        
        # Test 1: Initial challenge
        print(f"\n1️⃣ Initial challenge:")
        result, message = can_challenge(challenger, target)
        print(f"   Result: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 2: Create a match and test consecutive challenge
        print(f"\n2️⃣ After creating a match:")
        
        # Create match
        match = Match(
            team1_id=challenger.id,
            team2_id=target.id,
            status='confirmed',
            winner_id=challenger.id,
            created_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db.session.add(match)
        db.session.commit()
        
        print(f"   Created match: {challenger.team_name} vs {target.team_name}")
        
        # Test consecutive challenge
        result, message = can_challenge(challenger, target)
        print(f"   Consecutive challenge: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 3: Create another match with different opponent
        print(f"\n3️⃣ After playing different opponent:")
        
        # Find another opponent
        other_target = None
        for team in teams:
            if team.id != challenger.id and team.id != target.id:
                rank_diff = challenger.rank - team.rank
                if 1 <= rank_diff <= 3:
                    other_target = team
                    break
        
        if other_target:
            # Create another match
            match2 = Match(
                team1_id=challenger.id,
                team2_id=other_target.id,
                status='confirmed',
                winner_id=challenger.id,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(match2)
            db.session.commit()
            
            print(f"   Created match: {challenger.team_name} vs {other_target.team_name}")
            
            # Test challenge after playing different opponent
            result, message = can_challenge(challenger, target)
            print(f"   Challenge after other match: {'✅ Allowed' if result else '❌ Blocked'}")
            print(f"   Message: {message}")
        
        # Test 4: Platinum team exemption
        print(f"\n4️⃣ Platinum team exemption:")
        
        platinum_team = None
        platinum_target = None
        
        for team in teams:
            if team.tier == 'Platinum':
                platinum_team = team
                for t in teams:
                    if t.id != team.id:
                        rank_diff = team.rank - t.rank
                        if 1 <= rank_diff <= 3:
                            platinum_target = t
                            break
                if platinum_target:
                    break
        
        if platinum_team and platinum_target:
            print(f"   Platinum Challenger: {platinum_team.team_name}")
            print(f"   Platinum Target: {platinum_target.team_name}")
            
            # Create match for platinum team
            platinum_match = Match(
                team1_id=platinum_team.id,
                team2_id=platinum_target.id,
                status='confirmed',
                winner_id=platinum_team.id,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(platinum_match)
            db.session.commit()
            
            print(f"   Created match: {platinum_team.team_name} vs {platinum_target.team_name}")
            
            # Test consecutive challenge for platinum (should be allowed)
            result, message = can_challenge(platinum_team, platinum_target)
            print(f"   Platinum consecutive challenge: {'✅ Allowed' if result else '❌ Blocked'}")
            print(f"   Message: {message}")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        Match.query.filter_by(id=match.id).delete()
        if other_target:
            Match.query.filter_by(id=match2.id).delete()
        if platinum_team and platinum_target:
            Match.query.filter_by(id=platinum_match.id).delete()
        db.session.commit()
        
        print(f"\n✅ Test completed!")

if __name__ == '__main__':
    simple_consecutive_test() 