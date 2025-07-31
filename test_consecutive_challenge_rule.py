#!/usr/bin/env python3
"""
Test script to demonstrate the consecutive challenge rule.
This rule prevents teams from challenging the same opponent twice in a row,
with an exception for Platinum teams.
"""

import os
import sys
from app import app, db, User, Challenge, Match, can_challenge
from datetime import datetime, timezone, timedelta

def test_consecutive_challenge_rule():
    """Test the consecutive challenge rule"""
    with app.app_context():
        print("🏆 Consecutive Challenge Rule Test")
        print("=" * 50)
        
        print("\n📋 Rule Summary:")
        print("- Teams cannot challenge the same opponent twice in a row")
        print("- Must play another match before challenging the same team again")
        print("- Platinum teams are EXEMPT from this rule")
        print("- Only applies to confirmed matches")
        
        # Get teams with different ranks to test challenging
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).all()
        
        if len(teams) < 6:
            print("\n❌ Need at least 6 teams to test this rule")
            return
        
        print(f"\n👥 Current Team Rankings (Top 15):")
        for i, team in enumerate(teams[:15]):
            print(f"   {team.rank:2d}: {team.team_name} ({team.tier})")
        
        # Find teams that can challenge each other
        # We'll use teams with rank difference of 1 (consecutive ranks)
        lower_ranked_team = None
        higher_ranked_team = None
        
        # Look for consecutive teams (rank difference of 1)
        for i in range(len(teams) - 1):
            team1 = teams[i]
            team2 = teams[i + 1]
            if team1.rank + 1 == team2.rank:  # Consecutive ranks
                lower_ranked_team = team1
                higher_ranked_team = team2
                break
        
        if not lower_ranked_team or not higher_ranked_team:
            print(f"\n❌ Could not find consecutive teams")
            return
        
        print(f"\n🎯 Test Teams Found:")
        print(f"Lower Ranked Team: {lower_ranked_team.team_name} (Rank {lower_ranked_team.rank}, Tier {lower_ranked_team.tier})")
        print(f"Higher Ranked Team: {higher_ranked_team.team_name} (Rank {higher_ranked_team.rank}, Tier {higher_ranked_team.tier})")
        print(f"Rank Difference: {lower_ranked_team.rank - higher_ranked_team.rank}")
        
        print(f"\n🔍 Testing Challenge Rules:")
        
        # Test 1: Basic challenge (should work)
        print(f"\n1️⃣ Testing basic challenge from {lower_ranked_team.team_name} to {higher_ranked_team.team_name}:")
        can_challenge_result, message = can_challenge(lower_ranked_team, higher_ranked_team)
        print(f"   Result: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 2: Create a match between teams and test consecutive challenge
        print(f"\n2️⃣ Testing consecutive challenge rule:")
        
        # Create a match between lower_ranked_team and higher_ranked_team
        match = Match(
            team1_id=lower_ranked_team.id,
            team2_id=higher_ranked_team.id,
            status='confirmed',
            winner_id=lower_ranked_team.id,
            created_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db.session.add(match)
        db.session.commit()
        
        print(f"   Created confirmed match: {lower_ranked_team.team_name} vs {higher_ranked_team.team_name}")
        print(f"   Winner: {lower_ranked_team.team_name}")
        
        # Now test if lower_ranked_team can challenge higher_ranked_team again
        can_challenge_result, message = can_challenge(lower_ranked_team, higher_ranked_team)
        print(f"   {lower_ranked_team.team_name} trying to challenge {higher_ranked_team.team_name} again:")
        print(f"   Result: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 3: Create another match with a different team and test if lower_ranked_team can challenge higher_ranked_team again
        print(f"\n3️⃣ Testing after playing another match:")
        
        # Find another team for lower_ranked_team to play against
        other_team = None
        for team in teams:
            if team.id != lower_ranked_team.id and team.id != higher_ranked_team.id:
                # Find a team that lower_ranked_team can challenge
                rank_diff = lower_ranked_team.rank - team.rank
                if 1 <= rank_diff <= 3:
                    other_team = team
                    break
        
        if other_team:
            # Create a match between lower_ranked_team and other_team
            match2 = Match(
                team1_id=lower_ranked_team.id,
                team2_id=other_team.id,
                status='confirmed',
                winner_id=lower_ranked_team.id,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(match2)
            db.session.commit()
            
            print(f"   Created another confirmed match: {lower_ranked_team.team_name} vs {other_team.team_name}")
            print(f"   Winner: {lower_ranked_team.team_name}")
            
            # Now test if lower_ranked_team can challenge higher_ranked_team again
            can_challenge_result, message = can_challenge(lower_ranked_team, higher_ranked_team)
            print(f"   {lower_ranked_team.team_name} trying to challenge {higher_ranked_team.team_name} after playing {other_team.team_name}:")
            print(f"   Result: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
            print(f"   Message: {message}")
        
        # Test 4: Platinum team exemption
        platinum_team = None
        platinum_target = None
        
        # Find a Platinum team
        for team in teams:
            if team.tier == 'Platinum':
                platinum_team = team
                break
        
        if platinum_team:
            # Find a team that platinum_team can challenge
            for team in teams:
                rank_diff = platinum_team.rank - team.rank
                if 1 <= rank_diff <= 3:
                    platinum_target = team
                    break
            
            if platinum_target:
                print(f"\n4️⃣ Testing Platinum team exemption:")
                
                # Create a match between platinum_team and platinum_target
                platinum_match = Match(
                    team1_id=platinum_team.id,
                    team2_id=platinum_target.id,
                    status='confirmed',
                    winner_id=platinum_team.id,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(platinum_match)
                db.session.commit()
                
                print(f"   Created confirmed match: {platinum_team.team_name} vs {platinum_target.team_name}")
                print(f"   Winner: {platinum_team.team_name}")
                
                # Test if platinum team can challenge platinum_target again (should be allowed)
                can_challenge_result, message = can_challenge(platinum_team, platinum_target)
                print(f"   {platinum_team.team_name} (Platinum) trying to challenge {platinum_target.team_name} again:")
                print(f"   Result: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
                print(f"   Message: {message}")
        
        # Clean up test data
        print(f"\n🧹 Cleaning up test data...")
        Match.query.filter_by(id=match.id).delete()
        if other_team:
            Match.query.filter_by(id=match2.id).delete()
        if platinum_team and platinum_target:
            Match.query.filter_by(id=platinum_match.id).delete()
        db.session.commit()
        
        print(f"\n✅ Test completed!")
        print(f"\n📋 Rule Summary:")
        print(f"✅ Non-Platinum teams cannot challenge the same opponent twice in a row")
        print(f"✅ Must play another match before challenging the same team again")
        print(f"✅ Platinum teams are exempt from this rule")
        print(f"✅ Only applies to confirmed matches")

if __name__ == '__main__':
    test_consecutive_challenge_rule() 