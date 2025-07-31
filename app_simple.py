from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import csv
import io
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from zoneinfo import ZoneInfo
import os

# Set timezone to Lahore, Pakistan
LAHORE_TZ = ZoneInfo('Asia/Karachi')

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production database (Railway)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    # Fix for Railway PostgreSQL URLs
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
else:
    # Development database (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cpl.db'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

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

# Helper functions
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# Routes
@app.route('/')
def index():
    if get_current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            team_name = request.form.get('team_name')
            password = request.form.get('password')
            
            user = User.query.filter_by(team_name=team_name).first()
            
            if user and user.password_hash == password:
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid team name or password.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Login error: {e}")
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    try:
        current_user = get_current_user()
        
        if current_user:
            return render_template('dashboard.html', current_user=current_user)
        else:
            return render_template('dashboard.html', current_user=None)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return "Dashboard error", 500

# Initialize database
def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                admin = User(
                    team_name='Admin',
                    player1_name='Administrator',
                    player1_email='admin@cpl.com',
                    player2_name='Admin',
                    player2_email='admin@cpl.com',
                    password_hash='admin123',
                    is_admin=True,
                    rank=0,
                    tier='Admin',
                    status='active'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created!")
            
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

# Initialize database when app starts
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port) 