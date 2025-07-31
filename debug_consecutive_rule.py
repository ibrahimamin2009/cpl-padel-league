#!/usr/bin/env python3
"""
Debug script to understand the consecutive challenge rule.
"""

import os
import sys
from app import app, db, User, Challenge, Match, can_challenge
from datetime import datetime, timezone, timedelta

def debug_consecutive_rule():
    """Debug the consecutive challenge rule"""
    with app.app_context():
        print("🏆 Debug Consecutive Challenge Rule")
        print("=" * 50)
        
        # Get teams
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).limit(15).all()
        
        print(f"\n👥 Available Teams:")
        for i, team in enumerate(teams):
            print(f"   {i}: {team.rank} - {team.team_name} ({team.tier})")
        
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
        
        # Test initial challenge
        print(f"\n1️⃣ Initial challenge:")
        result, message = can_challenge(challenger, target)
        print(f"   Result: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Create a match
        print(f"\n2️⃣ Creating match...")
        match = Match(
            team1_id=challenger.id,
            team2_id=target.id,
            status='confirmed',
            winner_id=challenger.id,
            created_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db.session.add(match)
        db.session.commit()
        
        print(f"   Created match ID: {match.id}")
        print(f"   Match: {challenger.team_name} vs {target.team_name}")
        print(f"   Status: {match.status}")
        print(f"   Created at: {match.created_at}")
        
        # Debug: Check what matches exist for challenger
        print(f"\n3️⃣ Debugging matches for challenger:")
        challenger_matches = Match.query.filter(
            ((Match.team1_id == challenger.id) | (Match.team2_id == challenger.id)) &
            (Match.status == 'confirmed')
        ).order_by(Match.created_at.desc()).all()
        
        print(f"   Total confirmed matches for {challenger.team_name}: {len(challenger_matches)}")
        for m in challenger_matches:
            other_team_id = m.team1_id if m.team2_id == challenger.id else m.team2_id
            other_team = User.query.get(other_team_id)
            print(f"   - Match {m.id}: vs {other_team.team_name} (created: {m.created_at})")
        
        # Debug: Check recent match between challenger and target
        print(f"\n4️⃣ Debugging recent match between teams:")
        recent_match = Match.query.filter(
            ((Match.team1_id == challenger.id) & (Match.team2_id == target.id)) |
            ((Match.team1_id == target.id) & (Match.team2_id == challenger.id))
        ).filter(
            Match.status == 'confirmed'
        ).order_by(Match.created_at.desc()).first()
        
        if recent_match:
            print(f"   Found recent match: {recent_match.id}")
            print(f"   Created at: {recent_match.created_at}")
        else:
            print(f"   No recent match found between {challenger.team_name} and {target.team_name}")
        
        # Debug: Check challenger's most recent match
        print(f"\n5️⃣ Debugging challenger's most recent match:")
        challenging_team_recent_match = Match.query.filter(
            ((Match.team1_id == challenger.id) | (Match.team2_id == challenger.id)) &
            (Match.status == 'confirmed')
        ).order_by(Match.created_at.desc()).first()
        
        if challenging_team_recent_match:
            print(f"   Most recent match: {challenging_team_recent_match.id}")
            print(f"   Created at: {challenging_team_recent_match.created_at}")
            other_team_id = challenging_team_recent_match.team1_id if challenging_team_recent_match.team2_id == challenger.id else challenging_team_recent_match.team2_id
            other_team = User.query.get(other_team_id)
            print(f"   Against: {other_team.team_name}")
        else:
            print(f"   No recent match found for {challenger.team_name}")
        
        # Test consecutive challenge
        print(f"\n6️⃣ Testing consecutive challenge:")
        result, message = can_challenge(challenger, target)
        print(f"   Result: {'✅ Allowed' if result else '❌ Blocked'}")
        print(f"   Message: {message}")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        Match.query.filter_by(id=match.id).delete()
        db.session.commit()
        
        print(f"\n✅ Debug completed!")

if __name__ == '__main__':
    debug_consecutive_rule() 