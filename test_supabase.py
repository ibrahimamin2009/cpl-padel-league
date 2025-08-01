#!/usr/bin/env python3
"""
Test Supabase connection
"""
import os
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://qnoaemrurhhlslufficx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFub2FlbXJ1cmhobHNsdWZmaWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzM2NjQsImV4cCI6MjA2OTYwOTY2NH0.bWRrvX6HNDS--MoUH0wVaDDWZlV7sHuiUOanqIpAqSs"

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        print("✅ Supabase client created successfully!")
        
        # Test connection by trying to access the teams table
        try:
            response = supabase.table('teams').select('*').execute()
            print("✅ Successfully connected to Supabase!")
            print(f"📊 Found {len(response.data)} teams in database")
            
            if response.data:
                print("📋 Teams in database:")
                for team in response.data:
                    print(f"  - {team.get('team_name', 'Unknown')} (Admin: {team.get('is_admin', False)})")
            else:
                print("📋 No teams found in database")
                
        except Exception as e:
            print(f"⚠️  Could not access teams table: {e}")
            print("💡 This might be because the table doesn't exist yet")
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔗 Testing Supabase connection...")
    test_supabase_connection() 