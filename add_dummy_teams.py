#!/usr/bin/env python3
"""
Script to add 50 dummy teams to the CPL database.
This will create a realistic league with proper tier distribution.
"""

import os
import sys
from app import app, db, User, get_tier_for_rank, update_all_tiers
from datetime import datetime, timezone

def add_dummy_teams():
    """Add 50 dummy teams to the database"""
    with app.app_context():
        print("🏆 Adding 50 Dummy Teams to Chiniot Padel League")
        print("=" * 50)
        
        # Check current team count
        current_count = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).count()
        
        print(f"Current teams in database: {current_count}")
        
        if current_count > 0:
            print("⚠️  Database already has teams!")
            response = input("Do you want to continue and add more teams? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled.")
                return
        
        # Dummy team data with realistic names
        dummy_teams = [
            # Platinum Tier (Top 5) - Elite Teams
            ("ThunderStrike", "Alex", "alex@thunder.com", "Sarah", "sarah@thunder.com"),
            ("PhoenixRise", "Mike", "mike@phoenix.com", "Emma", "emma@phoenix.com"),
            ("DragonForce", "Chris", "chris@dragon.com", "Lisa", "lisa@dragon.com"),
            ("ShadowHunters", "David", "david@shadow.com", "Anna", "anna@shadow.com"),
            ("IronLegends", "Tom", "tom@iron.com", "Rachel", "rachel@iron.com"),
            
            # Gold Tier (Next 10) - Strong Teams
            ("SwiftStrikers", "James", "james@swift.com", "Maria", "maria@swift.com"),
            ("GoldenEagles", "Robert", "robert@golden.com", "Sophie", "sophie@golden.com"),
            ("SilverWolves", "Daniel", "daniel@silver.com", "Grace", "grace@silver.com"),
            ("CrimsonFalcons", "Andrew", "andrew@crimson.com", "Olivia", "olivia@crimson.com"),
            ("BlueThunder", "Steven", "steven@blue.com", "Chloe", "chloe@blue.com"),
            ("GreenRangers", "Kevin", "kevin@green.com", "Zoe", "zoe@green.com"),
            ("PurpleKnights", "Brian", "brian@purple.com", "Lily", "lily@purple.com"),
            ("OrangeCrushers", "Jason", "jason@orange.com", "Mia", "mia@orange.com"),
            ("RedDragons", "Eric", "eric@red.com", "Ava", "ava@red.com"),
            ("YellowBees", "Mark", "mark@yellow.com", "Ella", "ella@yellow.com"),
            
            # Silver Tier (Next 10) - Mid-tier Teams
            ("BronzeBears", "Paul", "paul@bronze.com", "Isabella", "isabella@bronze.com"),
            ("CopperLions", "Ryan", "ryan@copper.com", "Charlotte", "charlotte@copper.com"),
            ("SteelTigers", "Adam", "adam@steel.com", "Amelia", "amelia@steel.com"),
            ("IronEagles", "Justin", "justin@iron.com", "Harper", "harper@iron.com"),
            ("MetalFalcons", "Nathan", "nathan@metal.com", "Evelyn", "evelyn@metal.com"),
            ("CrystalWolves", "Sean", "sean@crystal.com", "Abigail", "abigail@crystal.com"),
            ("DiamondHawks", "Tyler", "tyler@diamond.com", "Emily", "emily@diamond.com"),
            ("RubyPanthers", "Brandon", "brandon@ruby.com", "Elizabeth", "elizabeth@ruby.com"),
            ("SapphireLions", "Dylan", "dylan@sapphire.com", "Sofia", "sofia@sapphire.com"),
            ("EmeraldTigers", "Connor", "connor@emerald.com", "Avery", "avery@emerald.com"),
            ("PearlEagles", "Caleb", "caleb@pearl.com", "Ella", "ella@pearl.com"),
            
            # Bronze Tier (Remaining 25) - Developing Teams
            ("CoalCrushers", "Hunter", "hunter@coal.com", "Scarlett", "scarlett@coal.com"),
            ("StoneStrikers", "Isaac", "isaac@stone.com", "Victoria", "victoria@stone.com"),
            ("RockRangers", "Jack", "jack@rock.com", "Madison", "madison@rock.com"),
            ("ClayCrushers", "Owen", "owen@clay.com", "Luna", "luna@clay.com"),
            ("SandStrikers", "Gavin", "gavin@sand.com", "Grace", "grace@sand.com"),
            ("DustRangers", "Lucas", "lucas@dust.com", "Chloe", "chloe@dust.com"),
            ("MudCrushers", "Evan", "evan@mud.com", "Penelope", "penelope@mud.com"),
            ("SoilStrikers", "Nicholas", "nicholas@soil.com", "Layla", "layla@soil.com"),
            ("EarthRangers", "Aaron", "aaron@earth.com", "Riley", "riley@earth.com"),
            ("GroundCrushers", "Charles", "charles@ground.com", "Nora", "nora@ground.com"),
            ("FloorStrikers", "Thomas", "thomas@floor.com", "Lily", "lily@floor.com"),
            ("BaseRangers", "Timothy", "timothy@base.com", "Hannah", "hannah@base.com"),
            ("FoundationCrushers", "Christian", "christian@foundation.com", "Zoe", "zoe@foundation.com"),
            ("RootStrikers", "Austin", "austin@root.com", "Stella", "stella@root.com"),
            ("CoreRangers", "Jose", "jose@core.com", "Aurora", "aurora@core.com"),
            ("CenterCrushers", "Ian", "ian@center.com", "Natalie", "natalie@center.com"),
            ("MiddleStrikers", "Kyle", "kyle@middle.com", "Addison", "addison@middle.com"),
            ("CentralRangers", "Jordan", "jordan@central.com", "Brooklyn", "brooklyn@central.com"),
            ("MainCrushers", "Cameron", "cameron@main.com", "Savannah", "savannah@main.com"),
            ("PrimaryStrikers", "Adrian", "adrian@primary.com", "Aria", "aria@primary.com"),
            ("FirstRangers", "Robert", "robert@first.com", "Ellie", "ellie@first.com"),
            ("LeadCrushers", "Jeremy", "jeremy@lead.com", "Skylar", "skylar@lead.com"),
            ("HeadStrikers", "Hunter", "hunter@head.com", "Lucy", "lucy@head.com"),
            ("TopRangers", "Trevor", "trevor@top.com", "Paisley", "paisley@top.com"),
            ("PeakCrushers", "Brendan", "brendan@peak.com", "Audrey", "audrey@peak.com"),
            ("SummitStrikers", "Peter", "peter@summit.com", "Bella", "bella@summit.com"),
            ("CrestRangers", "Ethan", "ethan@crest.com", "Claire", "claire@crest.com"),
            ("RidgeCrushers", "Carson", "carson@ridge.com", "Violet", "violet@ridge.com"),
            ("HillStrikers", "Blake", "blake@hill.com", "Savannah", "savannah@hill.com"),
            ("MountainRangers", "Jake", "jake@mountain.com", "Genesis", "genesis@mountain.com"),
            ("ValleyCrushers", "Max", "max@valley.com", "Faith", "faith@valley.com"),
            ("CanyonStrikers", "Sean", "sean@canyon.com", "Caroline", "caroline@canyon.com"),
            ("GorgeRangers", "Alex", "alex@gorge.com", "Kennedy", "kennedy@gorge.com"),
            ("RavineCrushers", "Tyler", "tyler@ravine.com", "Sadie", "sadie@ravine.com"),
            ("CliffStrikers", "Derek", "derek@cliff.com", "Gabriella", "gabriella@cliff.com"),
            ("BluffRangers", "Corey", "corey@bluff.com", "Adriana", "adriana@bluff.com"),
            ("RidgeCrushers2", "Marcus", "marcus@ridge2.com", "Gianna", "gianna@ridge2.com"),
            ("PeakStrikers2", "Phillip", "phillip@peak2.com", "Sophia", "sophia@peak2.com"),
            ("SummitRangers2", "Brett", "brett@summit2.com", "Allison", "allison@summit2.com"),
            ("CrestCrushers2", "Chad", "chad@crest2.com", "Mackenzie", "mackenzie@crest2.com"),
            ("HillStrikers2", "Todd", "todd@hill2.com", "Bailey", "bailey@hill2.com"),
            ("MountainCrushers2", "Dustin", "dustin@mountain2.com", "Brianna", "brianna@mountain2.com"),
            ("ValleyRangers2", "Dale", "dale@valley2.com", "Makayla", "makayla@valley2.com"),
            ("CanyonStrikers2", "Troy", "troy@canyon2.com", "Eva", "eva@canyon2.com"),
            ("GorgeCrushers2", "Lance", "lance@gorge2.com", "Taylor", "taylor@gorge2.com"),
            ("RavineRangers2", "Cody", "cody@ravine2.com", "Imani", "imani@ravine2.com"),
            ("CliffStrikers2", "Julian", "julian@cliff2.com", "Khloe", "khloe@cliff2.com"),
            ("BluffCrushers2", "Corey", "corey@bluff2.com", "Destiny", "destiny@bluff2.com"),
        ]
        
        print(f"\n📝 Adding {len(dummy_teams)} teams...")
        
        # Get the next available rank
        next_rank = db.session.query(db.func.max(User.rank)).scalar() or 0
        next_rank += 1
        
        teams_added = 0
        for team_data in dummy_teams:
            team_name, p1_name, p1_email, p2_name, p2_email = team_data
            
            # Check if team name already exists
            if User.query.filter_by(team_name=team_name).first():
                print(f"⚠️  Team '{team_name}' already exists, skipping...")
                continue
            
            # Determine tier based on rank
            tier = get_tier_for_rank(next_rank)
            
            # Create new team
            new_team = User(
                team_name=team_name,
                player1_name=p1_name,
                player1_email=p1_email,
                player2_name=p2_name,
                player2_email=p2_email,
                password_hash="password123",  # Simple password for dummy teams
                rank=next_rank,
                tier=tier,
                status='active'
            )
            
            db.session.add(new_team)
            next_rank += 1
            teams_added += 1
            
            if teams_added % 10 == 0:
                print(f"✅ Added {teams_added} teams so far...")
        
        # Commit all teams
        db.session.commit()
        
        # Update all tiers to ensure consistency
        update_all_tiers()
        
        print(f"\n🎉 Successfully added {teams_added} teams!")
        
        # Show tier distribution
        print("\n📊 Tier Distribution:")
        teams = User.query.filter(
            (User.status == 'active') & 
            (User.is_admin == False)
        ).order_by(User.rank).all()
        
        tier_counts = {}
        for team in teams:
            tier_counts[team.tier] = tier_counts.get(team.tier, 0) + 1
        
        for tier in ['Platinum', 'Gold', 'Silver', 'Bronze']:
            count = tier_counts.get(tier, 0)
            print(f"- {tier}: {count} teams")
        
        print(f"\n📈 Total teams in league: {len(teams)}")
        print("✅ All teams have been assigned appropriate tiers based on their rank!")

if __name__ == '__main__':
    # Confirm before proceeding
    print("⚠️  This will add 50 dummy teams to the database!")
    print("Teams will be created with:")
    print("- Realistic team names")
    print("- Proper tier assignment based on rank")
    print("- Simple password: 'password123'")
    print("- Active status")
    
    response = input("\nDo you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        add_dummy_teams()
    else:
        print("Operation cancelled.") 