#!/usr/bin/env python3
"""
Ultra-minimal Flask app for Vercel serverless deployment
Updated: 2025-08-01 - Force redeploy
"""
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Ensure the current directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, session

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Timezone
LAHORE_TZ = ZoneInfo('Asia/Karachi')

# Simple in-memory data storage (for demo purposes)
# This data will reset on every serverless invocation
teams = [
    {
        'id': 1,
        'team_name': 'admin',
        'password': 'admin',
        'is_admin': True,
        'status': 'active'
    }
]

# --- Routes ---

@app.route('/')
def index():
    """Home page - redirects to login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']
        
        user = next((t for t in teams if t['team_name'] == team_name), None)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid team name or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        team_name = request.form['team_name']
        password = request.form['password']
        
        if any(t['team_name'] == team_name for t in teams):
            flash('Team name already exists. Please choose another.', 'error')
        else:
            new_id = max([t['id'] for t in teams]) + 1 if teams else 1
            teams.append({
                'id': new_id,
                'team_name': team_name,
                'password': password,
                'is_admin': False,
                'status': 'active'
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    current_user = None
    if 'user_id' in session:
        current_user = next((t for t in teams if t['id'] == session['user_id']), None)
    
    if current_user:
        return render_template('dashboard.html', current_user=current_user, matches_played=0, matches_won=0, win_percentage=0, recent_matches=[], pending_challenges=[])
    else:
        return render_template('dashboard.html', current_user=None, total_teams=len(teams), active_teams=len(teams), recent_matches=[], pending_challenges=[])

@app.route('/rankings')
def rankings():
    """Rankings page"""
    return render_template('rankings.html', teams=teams)

@app.route('/analytics')
def analytics():
    """Admin analytics page"""
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('analytics.html', total_teams=len(teams), active_teams=len(teams))

@app.route('/health')
def health():
    """Health check endpoint"""
    return "OK", 200

# --- Error Handlers ---
@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    flash(f'An internal server error occurred: {error}', 'error')
    return render_template('error.html', error="Internal server error. Please try again."), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found."), 404

if __name__ == '__main__':
    app.run(debug=True) 