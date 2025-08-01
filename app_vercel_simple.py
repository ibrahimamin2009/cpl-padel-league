#!/usr/bin/env python3
"""
Simplest possible Flask app for Vercel - NO DATABASE
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Simple in-memory data (resets on each serverless invocation)
teams = [
    {
        'id': 1,
        'team_name': 'admin',
        'password': 'admin',
        'is_admin': True
    }
]

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        user = next((t for t in teams if t['team_name'] == team_name), None)
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        if any(t['team_name'] == team_name for t in teams):
            flash('Team exists', 'error')
        else:
            new_id = len(teams) + 1
            teams.append({
                'id': new_id,
                'team_name': team_name,
                'password': password,
                'is_admin': False
            })
            flash('Registered!', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = next((t for t in teams if t['id'] == session['user_id']), None)
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         current_user=user,
                         total_teams=len(teams))

@app.route('/ranking')
def ranking():
    return render_template('ranking.html', teams=teams)

@app.route('/analytics')
def analytics():
    if not session.get('is_admin'):
        flash('Admin only', 'error')
        return redirect(url_for('dashboard'))
    return render_template('analytics.html', total_teams=len(teams))

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True) 