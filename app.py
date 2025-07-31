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
    status = db.Column(db.String(20), default='active')  # active, frozen, inactive
    forfeit_count = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    
    # Relationships
    challenges_sent = db.relationship('Challenge', foreign_keys='Challenge.challenging_team_id', backref='challenging_team', lazy=True)
    challenges_received = db.relationship('Challenge', foreign_keys='Challenge.challenged_team_id', backref='challenged_team', lazy=True)
    matches_team1 = db.relationship('Match', foreign_keys='Match.team1_id', backref='team1', lazy=True)
    matches_team2 = db.relationship('Match', foreign_keys='Match.team2_id', backref='team2', lazy=True)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenging_team_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenged_team_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, expired, scheduled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    expires_at = db.Column(db.DateTime, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=True)

class TierConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(20), nullable=False, unique=True)
    max_rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ), onupdate=lambda: datetime.now(LAHORE_TZ))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, played, disputed, confirmed, forfeited
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(LAHORE_TZ))
    
    # Time limit fields
    match_deadline = db.Column(db.DateTime, nullable=True)  # 10 days from match creation
    score_deadline = db.Column(db.DateTime, nullable=True)  # 5 hours from match completion
    
    # Score fields
    set1_team1_score = db.Column(db.Integer, nullable=True)
    set1_team2_score = db.Column(db.Integer, nullable=True)
    set2_team1_score = db.Column(db.Integer, nullable=True)
    set2_team2_score = db.Column(db.Integer, nullable=True)
    set3_team1_score = db.Column(db.Integer, nullable=True)
    set3_team2_score = db.Column(db.Integer, nullable=True)
    
    # Venue coordination
    proposed_date = db.Column(db.DateTime, nullable=True)
    proposed_venue = db.Column(db.String(200), nullable=True)
    proposed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    venue_approved = db.Column(db.Boolean, nullable=True)
    venue_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Score approval fields
    score_entered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    score_approved = db.Column(db.Boolean, nullable=True)
    score_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    score_disputed = db.Column(db.Boolean, default=False)
    score_dispute_reason = db.Column(db.String(500), nullable=True)

# Helper function to get current user
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# Helper function to check if team can challenge
def can_challenge(challenging_team, challenged_team):
    # Admin accounts cannot participate in the league
    if challenging_team.is_admin:
        return False, "Admin accounts cannot participate in the league"
    if challenged_team.is_admin:
        return False, "Admin accounts cannot be challenged"
    
    # Check if challenging team can only challenge teams within 3 ranks ABOVE them
    rank_diff = challenging_team.rank - challenged_team.rank
    if rank_diff <= 0:
        return False, "You can only challenge teams ranked higher than you"
    if rank_diff > 3:
        return False, "You can only challenge teams within 3 ranks above you"
    
    # Check if challenging team already has a pending challenge
    existing_sent = Challenge.query.filter(
        (Challenge.challenging_team_id == challenging_team.id) & 
        (Challenge.status == 'pending')
    ).first()
    if existing_sent:
        return False, "You already have a pending challenge"
    
    # Check if challenging team has any active matches (scheduled or played but not confirmed)
    active_matches = Match.query.filter(
        ((Match.team1_id == challenging_team.id) | (Match.team2_id == challenging_team.id)) &
        (Match.status.in_(['scheduled', 'played']))
    ).first()
    if active_matches:
        return False, "You cannot challenge while you have an active match. Complete your current match first."
    
    # Check if challenged team has a pending challenge (received)
    existing_received = Challenge.query.filter(
        (Challenge.challenged_team_id == challenged_team.id) & 
        (Challenge.status == 'pending')
    ).first()
    if existing_received:
        # Check if the existing challenge is from a lower-ranked team
        existing_challenging_team = User.query.get(existing_received.challenging_team_id)
        if existing_challenging_team and existing_challenging_team.rank > challenged_team.rank:
            return False, "This team has a pending challenge from a lower-ranked team. They cannot receive another challenge until they respond to the current one."
        else:
            return False, "This team already has a pending challenge"
    
    # Check if challenged team has any active matches
    challenged_active_matches = Match.query.filter(
        ((Match.team1_id == challenged_team.id) | (Match.team2_id == challenged_team.id)) &
        (Match.status.in_(['scheduled', 'played']))
    ).first()
    if challenged_active_matches:
        return False, "This team has an active match. They cannot be challenged until their match is completed."
    
    # Check if challenged team has pending score entries for matches from lower-ranked teams
    pending_score_matches = Match.query.filter(
        ((Match.team1_id == challenged_team.id) | (Match.team2_id == challenged_team.id)) &
        (Match.status == 'played') &
        (Match.score_approved.is_(None))
    ).all()
    
    for match in pending_score_matches:
        # Check if the match is from a lower-ranked team
        other_team_id = match.team1_id if match.team2_id == challenged_team.id else match.team2_id
        other_team = User.query.get(other_team_id)
        if other_team and other_team.rank > challenged_team.rank:
            return False, "This team has pending score entries from lower-ranked teams"
    
    # Check if challenging team has recently played against the challenged team
    # This rule does not apply to Platinum teams
    if challenging_team.tier != 'Platinum':
        # Find the most recent completed match between these teams
        recent_match = Match.query.filter(
            ((Match.team1_id == challenging_team.id) & (Match.team2_id == challenged_team.id)) |
            ((Match.team1_id == challenged_team.id) & (Match.team2_id == challenging_team.id))
        ).filter(
            Match.status == 'confirmed'
        ).order_by(Match.created_at.desc()).first()
        
        if recent_match:
            # Check if this is the challenging team's most recent match
            challenging_team_recent_match = Match.query.filter(
                ((Match.team1_id == challenging_team.id) | (Match.team2_id == challenging_team.id)) &
                (Match.status == 'confirmed')
            ).order_by(Match.created_at.desc()).first()
            
            if challenging_team_recent_match and challenging_team_recent_match.id == recent_match.id:
                return False, "You cannot challenge the same team twice in a row. Play another match first."
    
    return True, "Challenge allowed"

# Time limit helper functions
def check_challenge_expiration():
    """Check and expire challenges that are older than 24 hours"""
    expired_challenges = Challenge.query.filter(
        (Challenge.status == 'pending') &
        (Challenge.expires_at < datetime.now(LAHORE_TZ))
    ).all()
    
    for challenge in expired_challenges:
        challenge.status = 'expired'
        # Count as forfeit for challenged team
        challenged_team = User.query.get(challenge.challenged_team_id)
        if challenged_team:
            challenged_team.forfeit_count += 1
            # Update ladder: challenging team moves up, challenged team moves down
            challenging_team = User.query.get(challenge.challenging_team_id)
            if challenging_team and challenging_team.rank > challenged_team.rank:
                challenging_team.rank = challenged_team.rank
                challenged_team.rank += 1
    
    db.session.commit()
    return len(expired_challenges)

def check_match_deadlines():
    """Check and forfeit matches that exceed the 10-day deadline"""
    now = datetime.now(LAHORE_TZ)
    overdue_matches = Match.query.filter(
        (Match.status == 'scheduled') &
        (Match.match_deadline.isnot(None)) &
        (Match.match_deadline < now)
    ).all()
    
    for match in overdue_matches:
        # Determine which team to forfeit (the one that didn't propose a venue)
        if match.proposed_by:
            # The team that didn't propose gets forfeited
            forfeited_team_id = match.team2_id if match.proposed_by == match.team1_id else match.team1_id
            winner_team_id = match.team1_id if match.proposed_by == match.team1_id else match.team2_id
            
            forfeited_team = User.query.get(forfeited_team_id)
            winner_team = User.query.get(winner_team_id)
            
            if forfeited_team and winner_team:
                forfeited_team.forfeit_count += 1
                match.status = 'forfeited'
                match.winner_id = winner_team_id
                
                # Update ladder
                update_ladder(winner_team, forfeited_team)
        else:
            # Both teams get forfeited if neither proposed
            team1 = User.query.get(match.team1_id)
            team2 = User.query.get(match.team2_id)
            
            if team1 and team2:
                team1.forfeit_count += 1
                team2.forfeit_count += 1
                match.status = 'forfeited'
    
    db.session.commit()
    return len(overdue_matches)

def check_score_deadlines():
    """Check and forfeit matches where scores weren't entered within 5 hours"""
    now = datetime.now(LAHORE_TZ)
    overdue_scores = Match.query.filter(
        (Match.status == 'played') &
        (Match.score_deadline.isnot(None)) &
        (Match.score_deadline < now) &
        (Match.score_approved.is_(None))
    ).all()
    
    for match in overdue_scores:
        # Determine which team to forfeit (the one that didn't enter the score)
        if match.score_entered_by:
            # The team that didn't enter the score gets forfeited
            forfeited_team_id = match.team2_id if match.score_entered_by == match.team1_id else match.team1_id
            winner_team_id = match.team1_id if match.score_entered_by == match.team1_id else match.team2_id
            
            forfeited_team = User.query.get(forfeited_team_id)
            winner_team = User.query.get(winner_team_id)
            
            if forfeited_team and winner_team:
                forfeited_team.forfeit_count += 1
                match.status = 'forfeited'
                match.winner_id = winner_team_id
                
                # Update ladder
                update_ladder(winner_team, forfeited_team)
        else:
            # Both teams get forfeited if neither entered score
            team1 = User.query.get(match.team1_id)
            team2 = User.query.get(match.team2_id)
            
            if team1 and team2:
                team1.forfeit_count += 1
                team2.forfeit_count += 1
                match.status = 'forfeited'
    
    db.session.commit()
    return len(overdue_scores)

def check_forfeit_demotions():
    """Check and demote teams that have 2 or more forfeits"""
    teams_to_demote = User.query.filter(
        (User.forfeit_count >= 2) &
        (User.status == 'active') &
        (User.is_admin == False)
    ).all()
    
    for team in teams_to_demote:
        # Move team to bottom of their tier or demote to lower tier
        current_tier = team.tier
        if current_tier == 'Platinum':
            team.tier = 'Gold'
        elif current_tier == 'Gold':
            team.tier = 'Silver'
        elif current_tier == 'Silver':
            team.tier = 'Bronze'
        else:  # Bronze - move to bottom of tier
            pass
        
        # Reset forfeit count after demotion
        team.forfeit_count = 0
        
        # Update rank to bottom of new tier
        update_all_tiers()
    
    db.session.commit()
    return len(teams_to_demote)

def validate_proposed_date(proposed_date):
    """Validate that proposed date is within 10 days of match creation"""
    now = datetime.now(LAHORE_TZ)
    max_date = now + timedelta(days=10)
    # If proposed_date is timezone-naive, assume it's in Lahore timezone
    if proposed_date.tzinfo is None:
        proposed_date = proposed_date.replace(tzinfo=LAHORE_TZ)
    return proposed_date <= max_date

def is_deadline_expired(deadline):
    """Check if a deadline has expired, handling timezone-aware comparison"""
    if not deadline:
        return False
    now = datetime.now(LAHORE_TZ)
    # If deadline is timezone-naive, assume it's in Lahore timezone
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=LAHORE_TZ)
    return deadline < now

# Helper function to determine tier based on rank
def get_tier_for_rank(rank):
    """Determine tier based on rank position using configurable tiers"""
    # Get tier configuration from database
    tier_configs = TierConfig.query.order_by(TierConfig.max_rank).all()
    
    if not tier_configs:
        # Fallback to default configuration if no config exists
        if rank <= 10:
            return 'Platinum'
        elif rank <= 30:
            return 'Gold'
        elif rank <= 60:
            return 'Silver'
        else:
            return 'Bronze'
    
    # Find the appropriate tier based on rank
    for config in tier_configs:
        if rank <= config.max_rank:
            return config.tier_name
    
    # If rank is higher than all configured tiers, return the last tier
    return tier_configs[-1].tier_name

def initialize_default_tiers():
    """Initialize default tier configuration if none exists"""
    if TierConfig.query.count() == 0:
        default_tiers = [
            {'tier_name': 'Platinum', 'max_rank': 10},
            {'tier_name': 'Gold', 'max_rank': 30},
            {'tier_name': 'Silver', 'max_rank': 60},
            {'tier_name': 'Bronze', 'max_rank': 999}  # High number for all remaining
        ]
        
        for tier_data in default_tiers:
            tier_config = TierConfig(**tier_data)
            db.session.add(tier_config)
        
        db.session.commit()

# Helper function to update tiers for all teams
def update_all_tiers():
    """Update tiers for all teams based on their current rank"""
    teams = User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).order_by(User.rank).all()
    
    for team in teams:
        new_tier = get_tier_for_rank(team.rank)
        if team.tier != new_tier:
            team.tier = new_tier
    
    db.session.commit()

# Helper function to update ladder after match
def update_ladder(winner, loser):
    # Simple ladder update - winner moves up, loser moves down
    if winner.rank > loser.rank:
        # Winner was lower ranked, so they move up
        winner.rank = loser.rank
        loser.rank += 1
        
        # Update tiers for all teams after rank changes
        update_all_tiers()
    else:
        # If no rank change, still update tiers in case there were other changes
        update_all_tiers()

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
            
            # Check if user exists and password matches (simple check for now)
            if user and user.password_hash == password:
                if user.status == 'pending':
                    flash('Your account is pending admin approval. Please wait for approval before logging in.', 'error')
                    return render_template('login.html')
                elif user.status == 'inactive':
                    flash('Your account has been rejected or deactivated. Please contact admin for assistance.', 'error')
                    return render_template('login.html')
                
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        player1_name = request.form.get('player1_name')
        player1_email = request.form.get('player1_email')
        player2_name = request.form.get('player2_name')
        player2_email = request.form.get('player2_email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([team_name, player1_name, player1_email, player2_name, player2_email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if team name exists
        if User.query.filter_by(team_name=team_name).first():
            flash('Team name already exists.', 'error')
            return render_template('register.html')
        
        # Check if emails exist
        if User.query.filter((User.player1_email == player1_email) | (User.player2_email == player1_email)).first():
            flash('Player 1 email already registered.', 'error')
            return render_template('register.html')
        
        if User.query.filter((User.player1_email == player2_email) | (User.player2_email == player2_email)).first():
            flash('Player 2 email already registered.', 'error')
            return render_template('register.html')
        
        # Create team with pending status (requires admin approval)
        new_team = User(
            team_name=team_name,
            player1_name=player1_name,
            player1_email=player1_email,
            player2_name=player2_name,
            player2_email=player2_email,
            password_hash=password,  # Simple password storage
            status='pending'  # Requires admin approval
        )
        
        db.session.add(new_team)
        db.session.commit()
        
        flash('Registration submitted successfully! Your account is pending admin approval. You will be notified when approved.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    try:
        current_user = get_current_user()
        
        # Run time limit checks
        expired_challenges = check_challenge_expiration()
        overdue_matches = check_match_deadlines()
        overdue_scores = check_score_deadlines()
        demoted_teams = check_forfeit_demotions()
        
        if current_user:
        # User-specific dashboard
        matches_played = Match.query.filter(
            ((Match.team1_id == current_user.id) | (Match.team2_id == current_user.id)) &
            (Match.status == 'confirmed')
        ).count()
        
        matches_won = Match.query.filter(
            (Match.winner_id == current_user.id) & (Match.status == 'confirmed')
        ).count()
        
        win_percentage = (matches_won / matches_played * 100) if matches_played > 0 else 0
        
        # Get recent matches for this team
        recent_matches = Match.query.filter(
            ((Match.team1_id == current_user.id) | (Match.team2_id == current_user.id))
        ).order_by(Match.created_at.desc()).limit(5).all()
        
        # Get pending challenges for this team
        pending_challenges = Challenge.query.filter(
            (Challenge.challenged_team_id == current_user.id) & (Challenge.status == 'pending')
        ).all()
        
        # Calculate display rank for current user (only for non-admin users)
        display_rank = None
        if not current_user.is_admin:
            all_teams = User.query.filter(
                (User.status == 'active') & 
                (User.is_admin == False)
            ).order_by(User.rank).all()
            
            for i, team in enumerate(all_teams, 1):
                if team.id == current_user.id:
                    display_rank = i
                    break
        
        return render_template('dashboard.html', 
                             current_user=current_user,
                             display_rank=display_rank,
                             matches_played=matches_played,
                             matches_won=matches_won,
                             win_percentage=win_percentage,
                             recent_matches=recent_matches,
                             pending_challenges=pending_challenges)
    else:
        # Public dashboard
        total_teams = User.query.count()
        active_teams = User.query.filter_by(status='active').count()
        recent_matches = Match.query.order_by(Match.created_at.desc()).limit(5).all()
        pending_challenges = Challenge.query.filter_by(status='pending').all()
        
        return render_template('dashboard.html', 
                             current_user=None,
                             total_teams=total_teams,
                             active_teams=active_teams,
                             recent_matches=recent_matches,
                             pending_challenges=pending_challenges)

@app.route('/analytics')
def analytics():
    current_user = get_current_user()
    
    # Overall statistics
    total_teams = User.query.count()
    active_teams = User.query.filter_by(status='active').count()
    total_matches = Match.query.count()
    played_matches = Match.query.filter_by(status='confirmed').count()
    
    # Tier distribution
    tier_stats = db.session.query(User.tier, db.func.count(User.id)).group_by(User.tier).all()
    
    # Recent activity
    recent_matches = Match.query.order_by(Match.created_at.desc()).limit(10).all()
    recent_challenges = Challenge.query.order_by(Challenge.created_at.desc()).limit(10).all()
    
    # Top teams by wins
    top_teams = db.session.query(
        User.team_name,
        db.func.count(Match.id).label('wins')
    ).join(Match, User.id == Match.winner_id).filter(
        Match.status == 'confirmed'
    ).group_by(User.id).order_by(db.func.count(Match.id).desc()).limit(5).all()
    
    return render_template('analytics.html',
                         current_user=current_user,
                         total_teams=total_teams,
                         active_teams=active_teams,
                         total_matches=total_matches,
                         played_matches=played_matches,
                         tier_stats=tier_stats,
                         recent_matches=recent_matches,
                         recent_challenges=recent_challenges,
                         top_teams=top_teams)

@app.route('/ranking')
def ranking():
    current_user = get_current_user()
    teams = User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).order_by(User.rank).all()
    
    # Reassign ranks to ensure they are sequential (1, 2, 3, ...)
    for i, team in enumerate(teams, 1):
        team.display_rank = i
    
    return render_template('ranking.html', teams=teams, current_user=current_user)

@app.route('/api/ranking')
def api_ranking():
    teams = User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).order_by(User.rank).all()
    ranking_data = []
    
    for i, team in enumerate(teams, 1):
        # Check if team has active matches
        active_matches = Match.query.filter(
            ((Match.team1_id == team.id) | (Match.team2_id == team.id)) &
            (Match.status.in_(['scheduled', 'played']))
        ).first()
        
        # Check if team has pending challenges
        pending_challenges = Challenge.query.filter(
            (Challenge.challenged_team_id == team.id) & 
            (Challenge.status == 'pending')
        ).first()
        
        # Check if team has pending score entries
        pending_scores = Match.query.filter(
            ((Match.team1_id == team.id) | (Match.team2_id == team.id)) &
            (Match.status == 'played') &
            (Match.score_approved.is_(None))
        ).first()
        
        status_info = {
            'available': True,
            'reason': None
        }
        
        if team.status == 'frozen':
            status_info = {
                'available': False,
                'reason': 'Frozen by admin'
            }
        elif active_matches:
            status_info = {
                'available': False,
                'reason': 'Active match in progress'
            }
        elif pending_challenges:
            status_info = {
                'available': False,
                'reason': 'Has pending challenge'
            }
        elif pending_scores:
            status_info = {
                'available': False,
                'reason': 'Pending score approval'
            }
        
        ranking_data.append({
            'id': team.id,
            'team_name': team.team_name,
            'rank': i,  # Use sequential display rank
            'tier': team.tier,
            'status': team.status,
            'forfeit_count': team.forfeit_count,
            'status_info': status_info
        })
    
    return jsonify(ranking_data)

@app.route('/matches')
def matches():
    current_user = get_current_user()
    
    if current_user:
        # User-specific matches
        team_matches = Match.query.filter(
            (Match.team1_id == current_user.id) | (Match.team2_id == current_user.id)
        ).order_by(Match.created_at.desc()).all()
        
        # All matches
        all_matches = Match.query.order_by(Match.created_at.desc()).limit(20).all()
        
        return render_template('matches.html', 
                             matches=team_matches,
                             all_matches=all_matches,
                             current_user=current_user,
                             now=datetime.now(LAHORE_TZ),
                             is_deadline_expired=is_deadline_expired)
    else:
        # All matches for public view
        matches = Match.query.order_by(Match.created_at.desc()).all()
        return render_template('matches.html', 
                             matches=matches,
                             all_matches=matches,
                             current_user=None,
                             now=datetime.now(LAHORE_TZ),
                             is_deadline_expired=is_deadline_expired)

@app.route('/challenge', methods=['GET', 'POST'])
def challenge():
    current_user = get_current_user()
    
    if not current_user:
        flash('You must be logged in to send challenges.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in the league.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        challenged_team_id = request.form.get('challenged_team_id')
        
        if not challenged_team_id:
            flash('Please select a team to challenge.', 'error')
            return redirect(url_for('challenge'))
        
        challenged_team = User.query.get(challenged_team_id)
        if not challenged_team:
            flash('Team not found.', 'error')
            return redirect(url_for('challenge'))
        
        # Check if challenge is allowed
        can_challenge_result, message = can_challenge(current_user, challenged_team)
        if not can_challenge_result:
            flash(message, 'error')
            return redirect(url_for('challenge'))
        

        
        # Create challenge
        new_challenge = Challenge(
            challenging_team_id=current_user.id,
            challenged_team_id=challenged_team_id,
            expires_at=datetime.now(LAHORE_TZ) + timedelta(hours=24)
        )
        
        db.session.add(new_challenge)
        db.session.commit()
        
        flash('Challenge sent successfully!', 'success')
        return redirect(url_for('challenge'))
    
    # Get available teams to challenge (only teams within 3 ranks ABOVE current team)
    all_teams = User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False) &
        (User.id != current_user.id) &
        (User.rank < current_user.rank) &  # Only teams ranked higher
        (User.rank >= current_user.rank - 3)  # Within 3 ranks above
    ).order_by(User.rank).all()
    
    # Filter teams that can actually be challenged
    available_teams = []
    for team in all_teams:
        can_challenge_result, message = can_challenge(current_user, team)
        if can_challenge_result:
            available_teams.append(team)
    
    # Get user's challenges
    sent_challenges = Challenge.query.filter(
        (Challenge.challenging_team_id == current_user.id) & 
        (Challenge.status == 'pending')
    ).all()
    
    received_challenges = Challenge.query.filter(
        (Challenge.challenged_team_id == current_user.id) & 
        (Challenge.status == 'pending')
    ).all()
    
    return render_template('challenge.html', 
                         teams=available_teams, 
                         current_user=current_user,
                         sent_challenges=sent_challenges,
                         received_challenges=received_challenges)

@app.route('/challenge/<int:challenge_id>/<action>')
def respond_to_challenge(challenge_id, action):
    current_user = get_current_user()
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if not current_user:
        flash('You must be logged in to respond to challenges.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in the league.', 'error')
        return redirect(url_for('challenge'))
    
    if challenge.challenged_team_id != current_user.id:
        flash('You can only respond to challenges sent to your team.', 'error')
        return redirect(url_for('challenge'))
    
    if action == 'accept':
        challenge.status = 'accepted'
        # Create match with 10-day deadline
        new_match = Match(
            team1_id=challenge.challenging_team_id,
            team2_id=challenge.challenged_team_id,
            status='scheduled',
            match_deadline=datetime.now(LAHORE_TZ) + timedelta(days=10)
        )
        db.session.add(new_match)
        challenge.match_id = new_match.id
        flash('Challenge accepted! Now coordinate venue and time. You have 10 days to complete this match.', 'success')
    elif action == 'reject':
        challenge.status = 'rejected'
        # Count as forfeit for challenged team and update ladder
        current_user.forfeit_count += 1
        
        # Update ladder: challenging team moves up, challenged team moves down
        challenging_team = User.query.get(challenge.challenging_team_id)
        if challenging_team and challenging_team.rank > current_user.rank:
            challenging_team.rank = current_user.rank
            current_user.rank += 1
        
        flash('Challenge rejected. This counts as a forfeit and ladder has been updated.', 'warning')
    
    db.session.commit()
    return redirect(url_for('challenge'))

@app.route('/match/<int:match_id>/venue', methods=['GET', 'POST'])
def propose_venue(match_id):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)
    
    if not current_user:
        flash('You must be logged in.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in matches.', 'error')
        return redirect(url_for('matches'))
    
    if current_user.id not in [match.team1_id, match.team2_id]:
        flash('You can only propose venues for your matches.', 'error')
        return redirect(url_for('matches'))
    
    if request.method == 'POST':
        venue = request.form.get('venue')
        date_str = request.form.get('date')
        
        if not venue or not date_str:
            flash('Please provide both venue and date.', 'error')
            return render_template('propose_venue.html', match=match, current_user=current_user)
        
        try:
            date = datetime.fromisoformat(date_str.replace('T', ' '))
        except:
            flash('Invalid date format.', 'error')
            return render_template('propose_venue.html', match=match, current_user=current_user)
        
        # Validate that proposed date is within 10 days of match creation
        if not validate_proposed_date(date):
            flash('Proposed date cannot exceed 10 days from match creation.', 'error')
            return render_template('propose_venue.html', match=match, current_user=current_user)
        
        match.proposed_venue = venue
        match.proposed_date = date
        match.proposed_by = current_user.id
        match.venue_approved = None
        
        db.session.commit()
        flash('Venue and time proposed! Waiting for opponent approval.', 'success')
        return redirect(url_for('matches'))
    
    return render_template('propose_venue.html', match=match, current_user=current_user)

@app.route('/match/<int:match_id>/venue/<action>')
def respond_venue(match_id, action):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)
    
    if not current_user:
        flash('You must be logged in.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in matches.', 'error')
        return redirect(url_for('matches'))
    
    if current_user.id not in [match.team1_id, match.team2_id]:
        flash('You can only respond to venue proposals for your matches.', 'error')
        return redirect(url_for('matches'))
    
    if action == 'approve':
        match.venue_approved = True
        match.venue_approved_by = current_user.id
        match.venue = match.proposed_venue
        match.date = match.proposed_date
        flash('Venue and time approved!', 'success')
    elif action == 'reject':
        match.venue_approved = False
        match.venue_approved_by = current_user.id
        match.proposed_venue = None
        match.proposed_date = None
        match.proposed_by = None
        flash('Venue and time rejected. Please propose new venue and time.', 'info')
    
    db.session.commit()
    return redirect(url_for('matches'))

@app.route('/match/<int:match_id>/score', methods=['GET', 'POST'])
def enter_score(match_id):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)
    
    if not current_user:
        flash('You must be logged in.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in matches.', 'error')
        return redirect(url_for('matches'))
    
    if current_user.id not in [match.team1_id, match.team2_id]:
        flash('You can only enter scores for your matches.', 'error')
        return redirect(url_for('matches'))
    
    if request.method == 'POST':
        set1_team1 = request.form.get('set1_team1')
        set1_team2 = request.form.get('set1_team2')
        set2_team1 = request.form.get('set2_team1')
        set2_team2 = request.form.get('set2_team2')
        set3_team1 = request.form.get('set3_team1')
        set3_team2 = request.form.get('set3_team2')
        
        if not all([set1_team1, set1_team2, set2_team1, set2_team2]):
            flash('First two sets are required.', 'error')
            return render_template('enter_score.html', match=match, current_user=current_user)
        
        try:
            match.set1_team1_score = int(set1_team1)
            match.set1_team2_score = int(set1_team2)
            match.set2_team1_score = int(set2_team1)
            match.set2_team2_score = int(set2_team2)
            
            if set3_team1 and set3_team2:
                match.set3_team1_score = int(set3_team1)
                match.set3_team2_score = int(set3_team2)
        except ValueError:
            flash('Please enter valid numbers for scores.', 'error')
            return render_template('enter_score.html', match=match, current_user=current_user)
        
        # Determine winner
        team1_sets = 0
        team2_sets = 0
        
        if match.set1_team1_score > match.set1_team2_score:
            team1_sets += 1
        else:
            team2_sets += 1
            
        if match.set2_team1_score > match.set2_team2_score:
            team1_sets += 1
        else:
            team2_sets += 1
            
        if match.set3_team1_score and match.set3_team2_score:
            if match.set3_team1_score > match.set3_team2_score:
                team1_sets += 1
            else:
                team2_sets += 1
        
        if team1_sets > team2_sets:
            match.winner_id = match.team1_id
        else:
            match.winner_id = match.team2_id
        
        # Set score approval status and 5-hour deadline
        match.score_entered_by = current_user.id
        match.score_approved = None  # Pending approval
        match.status = 'played'  # Changed from 'confirmed' to 'played'
        match.score_deadline = datetime.now(LAHORE_TZ) + timedelta(hours=5)
        
        db.session.commit()
        flash('Score entered successfully! Waiting for opponent approval. You have 5 hours to approve the score.', 'success')
        return redirect(url_for('matches'))
    
    return render_template('enter_score.html', match=match, current_user=current_user)

@app.route('/match/<int:match_id>/score/<action>')
def respond_score(match_id, action):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)
    
    if not current_user:
        flash('You must be logged in.', 'error')
        return redirect(url_for('login'))
    
    if current_user.is_admin:
        flash('Admin accounts cannot participate in matches.', 'error')
        return redirect(url_for('matches'))
    
    # Check if user is the other team in the match
    if current_user.id not in [match.team1_id, match.team2_id]:
        flash('You can only approve/reject scores for your matches.', 'error')
        return redirect(url_for('matches'))
    
    # Check if user is not the one who entered the score
    if current_user.id == match.score_entered_by:
        flash('You cannot approve/reject your own score entry.', 'error')
        return redirect(url_for('matches'))
    
    # Check if score is pending approval
    if match.score_approved is not None:
        flash('This score has already been processed.', 'error')
        return redirect(url_for('matches'))
    
    if action == 'approve':
        match.score_approved = True
        match.score_approved_by = current_user.id
        match.status = 'confirmed'
        
        # Update ladder
        winner = User.query.get(match.winner_id)
        loser = User.query.get(match.team1_id if match.winner_id == match.team2_id else match.team2_id)
        update_ladder(winner, loser)
        
        db.session.commit()
        flash('Score approved! Ladder updated.', 'success')
        
    elif action == 'reject':
        match.score_approved = False
        match.score_approved_by = current_user.id
        match.score_disputed = True
        match.status = 'disputed'
        
        db.session.commit()
        flash('Score rejected. Admin will review the dispute.', 'info')
    
    return redirect(url_for('matches'))

@app.route('/admin/score/<int:match_id>', methods=['GET', 'POST'])
def admin_enter_score(match_id):
    current_user = get_current_user()
    match = Match.query.get_or_404(match_id)
    
    if not current_user or not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if match is disputed
    if match.status != 'disputed':
        flash('This match is not disputed.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        set1_team1 = request.form.get('set1_team1')
        set1_team2 = request.form.get('set1_team2')
        set2_team1 = request.form.get('set2_team1')
        set2_team2 = request.form.get('set2_team2')
        set3_team1 = request.form.get('set3_team1')
        set3_team2 = request.form.get('set3_team2')
        
        if not all([set1_team1, set1_team2, set2_team1, set2_team2]):
            flash('First two sets are required.', 'error')
            return render_template('admin/enter_score.html', match=match, current_user=current_user)
        
        try:
            match.set1_team1_score = int(set1_team1)
            match.set1_team2_score = int(set1_team2)
            match.set2_team1_score = int(set2_team1)
            match.set2_team2_score = int(set2_team2)
            
            if set3_team1 and set3_team2:
                match.set3_team1_score = int(set3_team1)
                match.set3_team2_score = int(set3_team2)
        except ValueError:
            flash('Please enter valid numbers for scores.', 'error')
            return render_template('admin/enter_score.html', match=match, current_user=current_user)
        
        # Determine winner
        team1_sets = 0
        team2_sets = 0
        
        if match.set1_team1_score > match.set1_team2_score:
            team1_sets += 1
        else:
            team2_sets += 1
            
        if match.set2_team1_score > match.set2_team2_score:
            team1_sets += 1
        else:
            team2_sets += 1
            
        if match.set3_team1_score and match.set3_team2_score:
            if match.set3_team1_score > match.set3_team2_score:
                team1_sets += 1
            else:
                team2_sets += 1
        
        if team1_sets > team2_sets:
            match.winner_id = match.team1_id
        else:
            match.winner_id = match.team2_id
        
        match.status = 'confirmed'
        match.score_approved = True
        match.score_approved_by = current_user.id
        match.score_disputed = False
        
        # Update ladder
        winner = User.query.get(match.winner_id)
        loser = User.query.get(match.team1_id if match.winner_id == match.team2_id else match.team2_id)
        update_ladder(winner, loser)
        
        db.session.commit()
        flash('Score entered by admin! Ladder updated.', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/enter_score.html', match=match, current_user=current_user)

@app.route('/admin')
def admin_dashboard():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get pending registrations
    pending_teams = User.query.filter_by(status='pending').all()
    
    # Get all teams (excluding admin accounts)
    all_teams = User.query.filter(User.is_admin == False).all()
    
    # Get recent matches
    recent_matches = Match.query.order_by(Match.created_at.desc()).limit(10).all()
    
    # Get disputed matches
    disputed_matches = Match.query.filter_by(status='disputed').all()
    
    # Get matches pending score approval
    pending_score_approvals = Match.query.filter(
        Match.status == 'played',
        Match.score_approved.is_(None)
    ).all()
    
    # Get pending challenges
    pending_challenges = Challenge.query.filter_by(status='pending').all()
    
    # Get teams with pending score entries (unavailable for challenge)
    teams_with_pending_scores = []
    for team in User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).all():
        pending_matches = Match.query.filter(
            ((Match.team1_id == team.id) | (Match.team2_id == team.id)) &
            (Match.status == 'played') &
            (Match.score_approved.is_(None))
        ).all()
        
        if pending_matches:
            teams_with_pending_scores.append({
                'team': team,
                'pending_matches': pending_matches
            })
    
    # Get teams that have received challenges (unavailable)
    teams_with_challenges = []
    for team in User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).all():
        received_challenges = Challenge.query.filter(
            (Challenge.challenged_team_id == team.id) &
            (Challenge.status == 'pending')
        ).all()
        
        if received_challenges:
            teams_with_challenges.append({
                'team': team,
                'challenges': received_challenges
            })
    
    return render_template('admin/dashboard.html', 
                         pending_registrations=pending_teams,
                         teams=all_teams,
                         recent_matches=recent_matches,
                         disputed_matches=disputed_matches,
                         pending_score_approvals=pending_score_approvals,
                         pending_challenges=pending_challenges,
                         teams_with_pending_scores=teams_with_pending_scores,
                         teams_with_challenges=teams_with_challenges,
                         pending_freeze_requests=[],
                         active_teams=User.query.filter(
                             (User.status == 'active') & 
                             (User.is_admin == False)
                         ).all(),
                         total_matches=Match.query.count(),
                         pending_challenges_count=Challenge.query.filter_by(status='pending').count(),
                         current_user=current_user)

@app.route('/admin/registration/<int:team_id>/<action>')
def admin_registration_action(team_id, action):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    team = User.query.get_or_404(team_id)
    
    # Prevent approving admin accounts
    if team.is_admin:
        flash('Cannot approve admin accounts.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if action == 'approve':
        # Assign rank and tier when approving
        next_rank = db.session.query(db.func.max(User.rank)).scalar() or 0
        next_rank += 1
        
        team.status = 'active'
        team.rank = next_rank
        team.tier = get_tier_for_rank(next_rank)
        
        flash(f'Team {team.team_name} approved and assigned rank {next_rank}!', 'success')
    elif action == 'reject':
        team.status = 'inactive'
        flash(f'Team {team.team_name} rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/rankings', methods=['GET', 'POST'])
def admin_rankings():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Handle ranking updates
        for key, value in request.form.items():
            if key.startswith('rank_'):
                team_id = int(key.split('_')[1])
                new_rank = int(value)
                team = User.query.get(team_id)
                if team:
                    team.rank = new_rank
        
        db.session.commit()
        
        # Update tiers for all teams after rank changes
        update_all_tiers()
        
        flash('Rankings updated successfully!', 'success')
        return redirect(url_for('admin_rankings'))
    
    # Get all teams ordered by current rank (excluding admin accounts)
    teams = User.query.filter(
        (User.status == 'active') & 
        (User.is_admin == False)
    ).order_by(User.rank).all()
    
    # Reassign display ranks to ensure they are sequential (1, 2, 3, ...)
    for i, team in enumerate(teams, 1):
        team.display_rank = i
    
    return render_template('admin/rankings.html', teams=teams, current_user=current_user)

@app.route('/admin/tiers', methods=['GET', 'POST'])
def admin_tiers():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Clear existing tier configuration
        TierConfig.query.delete()
        
        # Get form data for each tier
        platinum_max = int(request.form.get('platinum_max', 10))
        gold_max = int(request.form.get('gold_max', 30))
        silver_max = int(request.form.get('silver_max', 60))
        bronze_max = int(request.form.get('bronze_max', 999))
        
        # Validate that max ranks are in ascending order
        if not (platinum_max < gold_max < silver_max < bronze_max):
            flash('Tier max ranks must be in ascending order (Platinum < Gold < Silver < Bronze).', 'error')
            return redirect(url_for('admin_tiers'))
        
        # Create new tier configuration
        tiers = [
            {'tier_name': 'Platinum', 'max_rank': platinum_max},
            {'tier_name': 'Gold', 'max_rank': gold_max},
            {'tier_name': 'Silver', 'max_rank': silver_max},
            {'tier_name': 'Bronze', 'max_rank': bronze_max}
        ]
        
        for tier_data in tiers:
            tier_config = TierConfig(**tier_data)
            db.session.add(tier_config)
        
        db.session.commit()
        
        # Update all team tiers with new configuration
        update_all_tiers()
        
        flash('Tier configuration updated successfully!', 'success')
        return redirect(url_for('admin_tiers'))
    
    # Get current tier configuration
    tier_configs = TierConfig.query.order_by(TierConfig.max_rank).all()
    current_config = {}
    for config in tier_configs:
        current_config[config.tier_name] = config.max_rank
    
    return render_template('admin/tiers.html', current_config=current_config, current_user=current_user)

@app.route('/admin/export')
def admin_export():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['CPL - Chiniot Padel League Complete Overview'])
    writer.writerow(['Generated on:', datetime.now(LAHORE_TZ).strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Teams Section
    writer.writerow(['TEAMS OVERVIEW'])
    writer.writerow(['ID', 'Team Name', 'Player 1', 'Player 1 Email', 'Player 2', 'Player 2 Email', 'Rank', 'Tier', 'Status', 'Forfeits', 'Created At'])
    
    teams = User.query.filter(User.is_admin == False).order_by(User.rank).all()
    for team in teams:
        writer.writerow([
            team.id,
            team.team_name,
            team.player1_name,
            team.player1_email,
            team.player2_name,
            team.player2_email,
            team.rank,
            team.tier,
            team.status,
            team.forfeit_count,
            team.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    writer.writerow([])
    
    # Challenges Section
    writer.writerow(['CHALLENGES OVERVIEW'])
    writer.writerow(['ID', 'Challenging Team', 'Challenged Team', 'Status', 'Created At', 'Expires At', 'Match ID'])
    
    challenges = Challenge.query.all()
    for challenge in challenges:
        writer.writerow([
            challenge.id,
            challenge.challenging_team.team_name if challenge.challenging_team else 'N/A',
            challenge.challenged_team.team_name if challenge.challenged_team else 'N/A',
            challenge.status,
            challenge.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            challenge.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            challenge.match_id or 'N/A'
        ])
    
    writer.writerow([])
    
    # Matches Section
    writer.writerow(['MATCHES OVERVIEW'])
    writer.writerow(['ID', 'Team 1', 'Team 2', 'Status', 'Winner', 'Venue', 'Date', 'Set 1 Score', 'Set 2 Score', 'Set 3 Score', 'Created At'])
    
    matches = Match.query.all()
    for match in matches:
        set1_score = f"{match.set1_team1_score}-{match.set1_team2_score}" if match.set1_team1_score is not None else 'N/A'
        set2_score = f"{match.set2_team1_score}-{match.set2_team2_score}" if match.set2_team1_score is not None else 'N/A'
        set3_score = f"{match.set3_team1_score}-{match.set3_team2_score}" if match.set3_team1_score is not None else 'N/A'
        
        writer.writerow([
            match.id,
            match.team1.team_name if match.team1 else 'N/A',
            match.team2.team_name if match.team2 else 'N/A',
            match.status,
            match.team1.team_name if match.winner_id == match.team1_id else (match.team2.team_name if match.winner_id == match.team2_id else 'N/A'),
            match.venue or 'N/A',
            match.date.strftime('%Y-%m-%d %H:%M:%S') if match.date else 'N/A',
            set1_score,
            set2_score,
            set3_score,
            match.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    writer.writerow([])
    
    # Analytics Section
    writer.writerow(['ANALYTICS OVERVIEW'])
    
    # Team statistics
    total_teams = User.query.filter(User.is_admin == False).count()
    active_teams = User.query.filter((User.status == 'active') & (User.is_admin == False)).count()
    total_matches = Match.query.count()
    played_matches = Match.query.filter_by(status='confirmed').count()
    
    writer.writerow(['Total Teams', total_teams])
    writer.writerow(['Active Teams', active_teams])
    writer.writerow(['Total Matches', total_matches])
    writer.writerow(['Played Matches', played_matches])
    writer.writerow(['Match Completion Rate', f"{(played_matches/total_matches*100):.1f}%" if total_matches > 0 else "0%"])
    
    writer.writerow([])
    
    # Tier distribution
    writer.writerow(['TIER DISTRIBUTION'])
    writer.writerow(['Tier', 'Count'])
    
    tier_stats = db.session.query(User.tier, db.func.count(User.id)).filter(
        User.is_admin == False
    ).group_by(User.tier).all()
    
    for tier, count in tier_stats:
        writer.writerow([tier, count])
    
    writer.writerow([])
    
    # Top teams by wins
    writer.writerow(['TOP TEAMS BY WINS'])
    writer.writerow(['Team Name', 'Wins'])
    
    top_teams = db.session.query(
        User.team_name,
        db.func.count(Match.id).label('wins')
    ).join(Match, User.id == Match.winner_id).filter(
        Match.status == 'confirmed'
    ).group_by(User.id).order_by(db.func.count(Match.id).desc()).limit(10).all()
    
    for team_name, wins in top_teams:
        writer.writerow([team_name, wins])
    
    # Prepare the response
    output.seek(0)
    
    # Create a BytesIO object for the response
    buffer = io.BytesIO()
    buffer.write(output.getvalue().encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'cpl_league_overview_{datetime.now(LAHORE_TZ).strftime("%Y%m%d_%H%M%S")}.csv',
        mimetype='text/csv'
    )

@app.route('/admin/challenges')
def admin_challenges():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all challenges with details
    all_challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    
    return render_template('admin/challenges.html', challenges=all_challenges, current_user=current_user)

@app.route('/admin/teams')
def admin_teams():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all teams (excluding admin accounts)
    teams = User.query.filter(User.is_admin == False).order_by(User.rank).all()
    
    # Reassign display ranks to ensure they are sequential (1, 2, 3, ...)
    for i, team in enumerate(teams, 1):
        team.display_rank = i
    
    return render_template('admin/teams.html', teams=teams, current_user=current_user)

@app.route('/admin/team/<int:team_id>/edit', methods=['GET', 'POST'])
def admin_edit_team(team_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    team = User.query.get_or_404(team_id)
    
    # Prevent editing admin accounts
    if team.is_admin:
        flash('Cannot edit admin accounts.', 'error')
        return redirect(url_for('admin_teams'))
    
    if request.method == 'POST':
        team.team_name = request.form['team_name']
        team.player1_name = request.form['player1_name']
        team.player1_email = request.form['player1_email']
        team.player2_name = request.form['player2_name']
        team.player2_email = request.form['player2_email']
        team.rank = int(request.form['rank'])
        team.status = request.form['status']
        team.forfeit_count = int(request.form['forfeit_count'])
        
        # Update tier based on new rank
        team.tier = get_tier_for_rank(team.rank)
        
        # Update tiers for all teams to ensure consistency
        update_all_tiers()
        
        flash(f'Team {team.team_name} updated successfully!', 'success')
        return redirect(url_for('admin_teams'))
    
    return render_template('admin/edit_team.html', team=team, current_user=current_user)

@app.route('/admin/team/<int:team_id>/delete', methods=['POST'])
def admin_delete_team(team_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    team = User.query.get_or_404(team_id)
    
    # Prevent deleting admin accounts
    if team.is_admin:
        flash('Cannot delete admin accounts.', 'error')
        return redirect(url_for('admin_teams'))
    
    # Check if team has any active challenges or matches
    active_challenges = Challenge.query.filter(
        ((Challenge.challenging_team_id == team_id) | (Challenge.challenged_team_id == team_id)) &
        (Challenge.status == 'pending')
    ).count()
    
    active_matches = Match.query.filter(
        ((Match.team1_id == team_id) | (Match.team2_id == team_id)) &
        (Match.status.in_(['scheduled', 'played']))
    ).count()
    
    if active_challenges > 0 or active_matches > 0:
        flash(f'Cannot delete team {team.team_name}. They have active challenges or matches.', 'error')
        return redirect(url_for('admin_teams'))
    
    team_name = team.team_name
    db.session.delete(team)
    db.session.commit()
    
    flash(f'Team {team_name} deleted successfully!', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/team/<int:team_id>/freeze', methods=['POST'])
def admin_freeze_team(team_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    team = User.query.get_or_404(team_id)
    
    # Prevent freezing admin accounts
    if team.is_admin:
        flash('Cannot freeze admin accounts.', 'error')
        return redirect(url_for('admin_teams'))
    
    team.status = 'frozen'
    db.session.commit()
    
    flash(f'Team {team.team_name} has been frozen.', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/team/<int:team_id>/unfreeze', methods=['POST'])
def admin_unfreeze_team(team_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    team = User.query.get_or_404(team_id)
    
    # Prevent unfreezing admin accounts
    if team.is_admin:
        flash('Cannot unfreeze admin accounts.', 'error')
        return redirect(url_for('admin_teams'))
    
    team.status = 'active'
    db.session.commit()
    
    flash(f'Team {team.team_name} has been unfrozen.', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/challenge/<int:challenge_id>/edit', methods=['GET', 'POST'])
def admin_edit_challenge(challenge_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if request.method == 'POST':
        challenge.status = request.form['status']
        challenge.expires_at = datetime.strptime(request.form['expires_at'], '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Challenge updated successfully!', 'success')
        return redirect(url_for('admin_challenges'))
    
    return render_template('admin/edit_challenge.html', challenge=challenge, current_user=current_user)

@app.route('/admin/challenge/<int:challenge_id>/delete', methods=['POST'])
def admin_delete_challenge(challenge_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Only allow deletion of pending challenges
    if challenge.status != 'pending':
        flash('Only pending challenges can be deleted.', 'error')
        return redirect(url_for('admin_challenges'))
    
    db.session.delete(challenge)
    db.session.commit()
    
    flash('Challenge deleted successfully!', 'success')
    return redirect(url_for('admin_challenges'))

@app.route('/admin/challenge/<int:challenge_id>/force_accept', methods=['POST'])
def admin_force_accept_challenge(challenge_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if challenge.status != 'pending':
        flash('Only pending challenges can be force accepted.', 'error')
        return redirect(url_for('admin_challenges'))
    
    # Create a match from the challenge
    match = Match(
        team1_id=challenge.challenging_team_id,
        team2_id=challenge.challenged_team_id,
        status='scheduled',
        created_at=datetime.now(LAHORE_TZ)
    )
    
    db.session.add(match)
    db.session.flush()  # Get the match ID
    
    # Update challenge status
    challenge.status = 'accepted'
    challenge.match_id = match.id
    
    db.session.commit()
    
    flash('Challenge force accepted and match created!', 'success')
    return redirect(url_for('admin_challenges'))

@app.route('/admin/challenge/<int:challenge_id>/force_reject', methods=['POST'])
def admin_force_reject_challenge(challenge_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    if challenge.status != 'pending':
        flash('Only pending challenges can be force rejected.', 'error')
        return redirect(url_for('admin_challenges'))
    
    challenge.status = 'rejected'
    db.session.commit()
    
    flash('Challenge force rejected!', 'success')
    return redirect(url_for('admin_challenges'))

@app.route('/admin/matches')
def admin_matches():
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all matches with details
    all_matches = Match.query.order_by(Match.created_at.desc()).all()
    
    return render_template('admin/matches.html', matches=all_matches, current_user=current_user)

@app.route('/admin/match/<int:match_id>/edit', methods=['GET', 'POST'])
def admin_edit_match(match_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    match = Match.query.get_or_404(match_id)
    
    if request.method == 'POST':
        match.status = request.form['status']
        match.venue = request.form['venue']
        match.winner_id = request.form.get('winner_id') if request.form.get('winner_id') else None
        
        # Parse date if provided
        if request.form.get('date'):
            try:
                match.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
            except:
                flash('Invalid date format.', 'error')
                return render_template('admin/edit_match.html', match=match, current_user=current_user)
        
        # Update scores
        if request.form.get('set1_team1_score'):
            match.set1_team1_score = int(request.form['set1_team1_score'])
        if request.form.get('set1_team2_score'):
            match.set1_team2_score = int(request.form['set1_team2_score'])
        if request.form.get('set2_team1_score'):
            match.set2_team1_score = int(request.form['set2_team1_score'])
        if request.form.get('set2_team2_score'):
            match.set2_team2_score = int(request.form['set2_team2_score'])
        if request.form.get('set3_team1_score'):
            match.set3_team1_score = int(request.form['set3_team1_score'])
        if request.form.get('set3_team2_score'):
            match.set3_team2_score = int(request.form['set3_team2_score'])
        
        # Update score approval
        match.score_approved = request.form.get('score_approved') == 'true'
        match.score_approved_by = current_user.id if match.score_approved else None
        
        db.session.commit()
        flash('Match updated successfully!', 'success')
        return redirect(url_for('admin_matches'))
    
    return render_template('admin/edit_match.html', match=match, current_user=current_user)

@app.route('/admin/match/<int:match_id>/delete', methods=['POST'])
def admin_delete_match(match_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    match = Match.query.get_or_404(match_id)
    
    # Check if match has been played
    if match.status == 'played' or match.status == 'confirmed':
        flash('Cannot delete a match that has been played.', 'error')
        return redirect(url_for('admin_matches'))
    
    # Delete associated challenge if exists
    challenge = Challenge.query.filter_by(match_id=match.id).first()
    if challenge:
        challenge.match_id = None
        challenge.status = 'expired'
    
    db.session.delete(match)
    db.session.commit()
    
    flash('Match deleted successfully!', 'success')
    return redirect(url_for('admin_matches'))

@app.route('/admin/match/<int:match_id>/force_complete', methods=['POST'])
def admin_force_complete_match(match_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    match = Match.query.get_or_404(match_id)
    
    if match.status != 'scheduled':
        flash('Only scheduled matches can be force completed.', 'error')
        return redirect(url_for('admin_matches'))
    
    match.status = 'confirmed'
    match.score_approved = True
    match.score_approved_by = current_user.id
    
    db.session.commit()
    
    flash('Match force completed!', 'success')
    return redirect(url_for('admin_matches'))

@app.route('/admin/match/<int:match_id>/reset', methods=['POST'])
def admin_reset_match(match_id):
    current_user = get_current_user()
    
    if current_user and not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    match = Match.query.get_or_404(match_id)
    
    # Reset match to scheduled status
    match.status = 'scheduled'
    match.winner_id = None
    match.set1_team1_score = None
    match.set1_team2_score = None
    match.set2_team1_score = None
    match.set2_team2_score = None
    match.set3_team1_score = None
    match.set3_team2_score = None
    match.score_entered_by = None
    match.score_approved = None
    match.score_approved_by = None
    match.score_disputed = False
    match.score_dispute_reason = None
    
    db.session.commit()
    
    flash('Match reset to scheduled status!', 'success')
    return redirect(url_for('admin_matches'))

# Create database tables
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Initialize default tier configuration
        initialize_default_tiers()
        
        # Update tiers for all existing teams
        update_all_tiers()

# Initialize database tables
def init_db():
    with app.app_context():
        db.create_all()
        # Initialize default tier configuration
        initialize_default_tiers()
        # Update tiers for all existing teams
        update_all_tiers()
        print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)