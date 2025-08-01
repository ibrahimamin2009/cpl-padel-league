#!/usr/bin/env python3
"""
Railway app with proper database handling
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import csv
import io
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# Set timezone to Lahore, Pakistan
LAHORE_TZ = ZoneInfo('Asia/Karachi')

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database configuration
if os.getenv('DATABASE_URL'):
    # Production database (Railway)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # Fix for Railway PostgreSQL URLs
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
elif os.getenv('RAILWAY_ENVIRONMENT'):
    # Force PostgreSQL on Railway even if DATABASE_URL is not set
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:EYUEkYWjVWzeFkqATysKdjZqXoonoBTm@metro.proxy.rlwy.net:59634/railway"
else:
    # Development database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cpl.db'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), unique=True, nullable=False)
    player1_name = db.Column(db.String(100), nullable=False)
    player1_email = db.Column(db.String(120), nullable=False)
    player2_name = db.Column(db.String(100), nullable=False)
    player2_email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    tier = db.Column(db.String(20), default='Bronze')
    rank = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    forfeit_count = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenging_team_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenged_team_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    expires_at = db.Column(db.DateTime, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=True)

class TierConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(20), nullable=False, unique=True)
    max_rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='scheduled')
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    match_deadline = db.Column(db.DateTime, nullable=True)
    score_deadline = db.Column(db.DateTime, nullable=True)
    set1_team1_score = db.Column(db.Integer, nullable=True)
    set1_team2_score = db.Column(db.Integer, nullable=True)
    set2_team1_score = db.Column(db.Integer, nullable=True)
    set2_team2_score = db.Column(db.Integer, nullable=True)
    set3_team1_score = db.Column(db.Integer, nullable=True)
    set3_team2_score = db.Column(db.Integer, nullable=True)
    proposed_date = db.Column(db.DateTime, nullable=True)
    proposed_venue = db.Column(db.String(200), nullable=True)
    proposed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    venue_approved = db.Column(db.Boolean, nullable=True)
    venue_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    score_entered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    score_approved = db.Column(db.Boolean, nullable=True)
    score_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    score_disputed = db.Column(db.Boolean, default=False)
    score_dispute_reason = db.Column(db.String(500), nullable=True)

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        password = request.form.get('password')
        
        user = User.query.filter_by(team_name=team_name).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.status == 'pending':
                flash('Your account is pending admin approval. Please wait for approval before logging in.', 'error')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['team_name'] = user.team_name
            session['is_admin'] = user.is_admin
            
            if user.is_admin:
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid team name or password.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('admin/dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000) 