#!/usr/bin/env python3
"""
Flask app with Supabase integration for Vercel deployment
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from supabase import create_client, Client
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

# Fallback in-memory data if Supabase not configured
teams = [
    {
        'id': 1,
        'team_name': 'admin',
        'password': 'admin',
        'is_admin': True,
        'status': 'active'
    }
]

def get_teams():
    """Get teams from Supabase or fallback to in-memory"""
    if supabase:
        try:
            response = supabase.table('teams').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Supabase error: {e}")
            return teams
    return teams

def add_team(team_data):
    """Add team to Supabase or fallback to in-memory"""
    if supabase:
        try:
            response = supabase.table('teams').insert(team_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Supabase error: {e}")
            return None
    
    # Fallback to in-memory
    new_id = len(teams) + 1
    team_data['id'] = new_id
    teams.append(team_data)
    return team_data

def find_team(team_name):
    """Find team by name"""
    if supabase:
        try:
            response = supabase.table('teams').select('*').eq('team_name', team_name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Supabase error: {e}")
            return None
    
    # Fallback to in-memory
    return next((t for t in teams if t['team_name'] == team_name), None)

@app.route('/')
def index():
    """Home page"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        user = find_team(team_name)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['team_name'] = user['team_name']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid team name or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        # Check if team exists
        existing_teams = get_teams()
        if any(t['team_name'] == team_name for t in existing_teams):
            flash('Team name already exists', 'error')
        else:
            # Add new team
            new_team = {
                'team_name': team_name,
                'password': password,
                'is_admin': False,
                'status': 'active',
                'created_at': datetime.now(LAHORE_TZ).isoformat()
            }
            
            result = add_team(new_team)
            if result:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = find_team(session.get('team_name'))
    if not user:
        return redirect(url_for('login'))
    
    all_teams = get_teams()
    return render_template('dashboard.html', 
                         current_user=user,
                         total_teams=len(all_teams),
                         active_teams=len([t for t in all_teams if t['status'] == 'active']),
                         recent_matches=[],
                         pending_challenges=[])

@app.route('/ranking')
def ranking():
    """Ranking page"""
    teams = get_teams()
    return render_template('ranking.html', teams=teams)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    teams = get_teams()
    return render_template('analytics.html', 
                         total_teams=len(teams),
                         active_teams=len([t for t in teams if t['status'] == 'active']),
                         total_matches=0,
                         total_challenges=0)

@app.route('/api/ranking')
def api_ranking():
    """API endpoint for ranking"""
    teams = get_teams()
    return {'teams': teams}

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    return render_template('error.html', error="Internal server error. Please try again."), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found."), 404

if __name__ == '__main__':
    app.run(debug=True) 