#!/usr/bin/env python3
"""
Demonstration of the consecutive challenge rule.
This rule prevents teams from challenging the same opponent twice in a row,
with an exception for Platinum teams.
"""

import os
import sys
from app import app, db, User, Challenge, Match, can_challenge
from datetime import datetime, timezone, timedelta

def demo_consecutive_rule():
    """Demonstrate the consecutive challenge rule"""
    with app.app_context():
        print("🏆 Consecutive Challenge Rule Demonstration")
        print("=" * 50)
        
        print("\n📋 Rule Summary:")
        print("- Teams cannot challenge the same opponent twice in a row")
        print("- Must play another match before challenging the same team again")
        print("- Platinum teams are EXEMPT from this rule")
        print("- Only applies to confirmed matches")
        
        # Get some teams for demonstration
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).limit(10).all()
        
        if len(teams) < 4:
            print("\n❌ Need at least 4 teams to demonstrate this rule")
            return
        
        print(f"\n👥 Available Teams:")
        for i, team in enumerate(teams[:5]):
            print(f"   {team.rank:2d}: {team.team_name} ({team.tier})")
        
        # Create a simple demonstration
        print(f"\n🎯 Rule Demonstration:")
        
        # Scenario 1: Non-Platinum team tries to challenge same opponent twice
        non_platinum_team = None
        target_team = None
        
        # Find a non-Platinum team and a target
        for team in teams:
            if team.tier != 'Platinum':
                non_platinum_team = team
                # Find a team they can challenge
                for target in teams:
                    if target.id != team.id:
                        rank_diff = team.rank - target.rank
                        if 1 <= rank_diff <= 3:
                            target_team = target
                            break
                if target_team:
                    break
        
        if non_platinum_team and target_team:
            print(f"\n1️⃣ Scenario: Non-Platinum team challenging same opponent twice")
            print(f"   Challenger: {non_platinum_team.team_name} (Rank {non_platinum_team.rank}, Tier {non_platinum_team.tier})")
            print(f"   Target: {target_team.team_name} (Rank {target_team.rank}, Tier {target_team.tier})")
            
            # Test initial challenge
            can_challenge_result, message = can_challenge(non_platinum_team, target_team)
            print(f"   Initial challenge: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
            print(f"   Message: {message}")
            
            # Create a match between them
            match = Match(
                team1_id=non_platinum_team.id,
                team2_id=target_team.id,
                status='confirmed',
                winner_id=non_platinum_team.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=1)
            )
            db.session.add(match)
            db.session.commit()
            
            print(f"   Created confirmed match: {non_platinum_team.team_name} vs {target_team.team_name}")
            
            # Test consecutive challenge (should be blocked)
            can_challenge_result, message = can_challenge(non_platinum_team, target_team)
            print(f"   Consecutive challenge: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
            print(f"   Message: {message}")
            
            # Create another match with different opponent
            other_team = None
            for team in teams:
                if team.id != non_platinum_team.id and team.id != target_team.id:
                    rank_diff = non_platinum_team.rank - team.rank
                    if 1 <= rank_diff <= 3:
                        other_team = team
                        break
            
            if other_team:
                match2 = Match(
                    team1_id=non_platinum_team.id,
                    team2_id=other_team.id,
                    status='confirmed',
                    winner_id=non_platinum_team.id,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(match2)
                db.session.commit()
                
                print(f"   Created another match: {non_platinum_team.team_name} vs {other_team.team_name}")
                
                # Test challenge after playing different opponent (should be allowed)
                can_challenge_result, message = can_challenge(non_platinum_team, target_team)
                print(f"   Challenge after other match: {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
                print(f"   Message: {message}")
            
            # Clean up
            Match.query.filter_by(id=match.id).delete()
            if other_team:
                Match.query.filter_by(id=match2.id).delete()
            db.session.commit()
        
        # Scenario 2: Platinum team exemption
        platinum_team = None
        platinum_target = None
        
        # Find a Platinum team
        for team in teams:
            if team.tier == 'Platinum':
                platinum_team = team
                # Find a team they can challenge
                for target in teams:
                    if target.id != team.id:
                        rank_diff = team.rank - target.rank
                        if 1 <= rank_diff <= 3:
                            platinum_target = target
                            break
                if platinum_target:
                    break
        
        if platinum_team and platinum_target:
            print(f"\n2️⃣ Scenario: Platinum team exemption")
            print(f"   Challenger: {platinum_team.team_name} (Rank {platinum_team.rank}, Tier {platinum_team.tier})")
            print(f"   Target: {platinum_target.team_name} (Rank {platinum_target.rank}, Tier {platinum_target.tier})")
            
            # Create a match between platinum team and target
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
            
            # Test consecutive challenge (should be allowed for Platinum)
            can_challenge_result, message = can_challenge(platinum_team, platinum_target)
            print(f"   Consecutive challenge (Platinum): {'✅ Allowed' if can_challenge_result else '❌ Blocked'}")
            print(f"   Message: {message}")
            
            # Clean up
            Match.query.filter_by(id=platinum_match.id).delete()
            db.session.commit()
        
        print(f"\n✅ Demonstration completed!")
        print(f"\n📋 Rule Summary:")
        print(f"✅ Non-Platinum teams cannot challenge the same opponent twice in a row")
        print(f"✅ Must play another match before challenging the same team again")
        print(f"✅ Platinum teams are exempt from this rule")
        print(f"✅ Only applies to confirmed matches")

if __name__ == '__main__':
    demo_consecutive_rule() 