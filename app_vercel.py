#!/usr/bin/env python3
"""
Simplified Flask app for Vercel serverless deployment
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

# Simple in-memory data storage (for demo purposes)
teams = [
    {
        'id': 1,
        'team_name': 'admin',
        'password': 'admin',
        'is_admin': True,
        'status': 'active'
    }
]

matches = []
challenges = []

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
        
        # Find user
        user = next((team for team in teams if team['team_name'] == team_name), None)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['team_name'] = user['team_name']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid team name or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = next((team for team in teams if team['id'] == session['user_id']), None)
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         current_user=user,
                         total_teams=len(teams),
                         active_teams=len([t for t in teams if t['status'] == 'active']),
                         recent_matches=matches[-5:] if matches else [],
                         pending_challenges=[c for c in challenges if c['status'] == 'pending'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        # Check if team already exists
        if any(team['team_name'] == team_name for team in teams):
            flash('Team name already exists', 'error')
        else:
            # Add new team
            new_team = {
                'id': len(teams) + 1,
                'team_name': team_name,
                'password': password,
                'is_admin': False,
                'status': 'active'
            }
            teams.append(new_team)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/challenge')
def challenge():
    """Challenge page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('challenge.html', 
                         teams=[t for t in teams if t['id'] != session['user_id']],
                         challenges=challenges)

@app.route('/matches')
def matches():
    """Matches page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('matches.html', matches=matches)

@app.route('/ranking')
def ranking():
    """Ranking page"""
    return render_template('ranking.html', teams=teams)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('analytics.html', 
                         total_teams=len(teams),
                         active_teams=len([t for t in teams if t['status'] == 'active']),
                         total_matches=len(matches),
                         total_challenges=len(challenges))

@app.route('/api/ranking')
def api_ranking():
    """API endpoint for ranking"""
    return {'teams': teams}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 