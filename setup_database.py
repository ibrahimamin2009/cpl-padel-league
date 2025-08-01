#!/usr/bin/env python3
"""
Setup database tables in Supabase
"""
import os
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://qnoaemrurhhlslufficx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFub2FlbXJ1cmhobHNsdWZmaWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzM2NjQsImV4cCI6MjA2OTYwOTY2NH0.bWRrvX6HNDS--MoUH0wVaDDWZlV7sHuiUOanqIpAqSs"

def setup_database():
    """Setup database tables"""
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        print("✅ Supabase client created successfully!")
        
        # Create teams table
        print("📋 Creating teams table...")
        
        # Insert admin user
        admin_team = {
            'team_name': 'admin',
            'password': 'admin',
            'is_admin': True,
            'status': 'active'
        }
        
        try:
            response = supabase.table('teams').insert(admin_team).execute()
            print("✅ Admin user created successfully!")
            print(f"📊 Admin user ID: {response.data[0]['id']}")
        except Exception as e:
            print(f"⚠️  Could not create admin user: {e}")
            print("💡 The table might already exist or have the admin user")
        
        # Test reading teams
        try:
            response = supabase.table('teams').select('*').execute()
            print(f"✅ Successfully read {len(response.data)} teams from database")
            
            if response.data:
                print("📋 Teams in database:")
                for team in response.data:
                    print(f"  - {team.get('team_name', 'Unknown')} (Admin: {team.get('is_admin', False)})")
                    
        except Exception as e:
            print(f"❌ Could not read teams: {e}")
            
    except Exception as e:
        print(f"❌ Failed to setup database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔗 Setting up Supabase database...")
    setup_database() 