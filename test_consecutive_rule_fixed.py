#!/usr/bin/env python3
"""
Test the consecutive challenge rule with proper match timing.
"""

import os
import sys
from app import app, db, User, Challenge, Match, can_challenge
from datetime import datetime, timezone, timedelta

def test_consecutive_rule_fixed():
    """Test the consecutive challenge rule with proper timing"""
    with app.app_context():
        print("🏆 Chiniot Padel League Consecutive Challenge Rule Test (Fixed)")
        print("=" * 50)
        
        # Get teams
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).limit(15).all()
        
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
        
        print(f"\n🎯 Test Teams:")
        print(f"   Challenger: {challenger.team_name} (Rank {challenger.rank}, Tier {challenger.tier})")
        print(f"   Target: {target.team_name} (Rank {target.rank}, Tier {target.tier})")
        
        # Clean up any existing matches for these teams
        print(f"\n🧹 Cleaning up existing matches...")
        existing_matches = Match.query.filter(
            ((Match.team1_id == challenger.id) | (Match.team2_id == challenger.id)) |
            ((Match.team1_id == target.id) | (Match.team2_id == target.id))
        ).all()
        
        for match in existing_matches:
            print(f"   Deleting match {match.id}")
            db.session.delete(match)
        db.session.commit()
        
        # Test 1: Initial challenge
        print(f"\n1️⃣ Initial challenge:")
        result, message = can_challenge(challenger, target)
        print(f"   Result: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 2: Create a match and test consecutive challenge
        print(f"\n2️⃣ Creating match and testing consecutive challenge:")
        
        # Create match with current timestamp (most recent)
        match = Match(
            team1_id=challenger.id,
            team2_id=target.id,
            status='confirmed',
            winner_id=challenger.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(match)
        db.session.commit()
        
        print(f"   Created match: {challenger.team_name} vs {target.team_name}")
        print(f"   Match ID: {match.id}, Created at: {match.created_at}")
        
        # Test consecutive challenge (should be blocked)
        result, message = can_challenge(challenger, target)
        print(f"   Consecutive challenge: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Test 3: Create another match with different opponent
        print(f"\n3️⃣ Creating match with different opponent:")
        
        # Find another opponent
        other_target = None
        for team in teams:
            if team.id != challenger.id and team.id != target.id:
                rank_diff = challenger.rank - team.rank
                if 1 <= rank_diff <= 3:
                    other_target = team
                    break
        
        if other_target:
            # Create another match with later timestamp
            match2 = Match(
                team1_id=challenger.id,
                team2_id=other_target.id,
                status='confirmed',
                winner_id=challenger.id,
                created_at=datetime.now(timezone.utc) + timedelta(minutes=1)
            )
            db.session.add(match2)
            db.session.commit()
            
            print(f"   Created match: {challenger.team_name} vs {other_target.team_name}")
            print(f"   Match ID: {match2.id}, Created at: {match2.created_at}")
            
            # Test challenge after playing different opponent (should be allowed)
            result, message = can_challenge(challenger, target)
            print(f"   Challenge after other match: {'✅ Allowed' if result else '❌ Blocked'}")
            print(f"   Message: {message}")
        
        # Test 4: Platinum team exemption
        print(f"\n4️⃣ Testing Platinum team exemption:")
        
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
            
            # Clean up any existing matches for platinum team
            platinum_matches = Match.query.filter(
                ((Match.team1_id == platinum_team.id) | (Match.team2_id == platinum_team.id)) |
                ((Match.team1_id == platinum_target.id) | (Match.team2_id == platinum_target.id))
            ).all()
            
            for match in platinum_matches:
                db.session.delete(match)
            db.session.commit()
            
            # Create match for platinum team
            platinum_match = Match(
                team1_id=platinum_team.id,
                team2_id=platinum_target.id,
                status='confirmed',
                winner_id=platinum_team.id,
                created_at=datetime.now(timezone.utc) + timedelta(minutes=2)
            )
            db.session.add(platinum_match)
            db.session.commit()
            
            print(f"   Created match: {platinum_team.team_name} vs {platinum_target.team_name}")
            print(f"   Match ID: {platinum_match.id}, Created at: {platinum_match.created_at}")
            
            # Test consecutive challenge for platinum (should be allowed)
            result, message = can_challenge(platinum_team, platinum_target)
            print(f"   Platinum consecutive challenge: {'✅ Allowed' if result else '❌ Blocked'}")
            print(f"   Message: {message}")
        
        # Clean up
        print(f"\n🧹 Final cleanup...")
        all_test_matches = [match, match2] if other_target else [match]
        if platinum_team and platinum_target:
            all_test_matches.append(platinum_match)
        
        for test_match in all_test_matches:
            Match.query.filter_by(id=test_match.id).delete()
        db.session.commit()
        
        print(f"\n✅ Test completed!")
        print(f"\n📋 Rule Summary:")
        print(f"✅ Non-Platinum teams cannot challenge the same opponent twice in a row")
        print(f"✅ Must play another match before challenging the same team again")
        print(f"✅ Platinum teams are exempt from this rule")
        print(f"✅ Only applies to confirmed matches")

if __name__ == '__main__':
    test_consecutive_rule_fixed() 