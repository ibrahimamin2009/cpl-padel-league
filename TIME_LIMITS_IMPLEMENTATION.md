# CPL Time Limits Implementation

This document describes the implementation of time limits and forfeit rules in the CPL (Competitive Pickleball League) application.

## Overview

The following time limits have been implemented to ensure fair play and timely match completion. All times are in **Lahore, Pakistan timezone (Asia/Karachi)**:


1. **24 hours to respond to challenges**
2. **10 days to play accepted matches**
3. **5 hours to enter scores after match time**
4. **No date can be proposed if it exceeds the 10-day window**
5. **2 forfeits = automatic demotion**

## Database Changes

### New Fields Added to Match Table

- `match_deadline`: DateTime field for 10-day match completion deadline
- `score_deadline`: DateTime field for 5-hour score entry deadline

### Updated Status Values

- Added `'forfeited'` to the match status options

## Implementation Details

### Timezone Configuration

All datetime operations use Lahore, Pakistan timezone (Asia/Karachi):
```python
from zoneinfo import ZoneInfo
LAHORE_TZ = ZoneInfo('Asia/Karachi')
```

### 1. Challenge Expiration (24 hours)

**Location**: `check_challenge_expiration()` function

**Behavior**:
- Automatically expires challenges older than 24 hours
- Counts as forfeit for the challenged team
- Updates ladder: challenging team moves up, challenged team moves down

**Code Flow**:
```python
def check_challenge_expiration():
    expired_challenges = Challenge.query.filter(
        (Challenge.status == 'pending') &
        (Challenge.expires_at < datetime.now(LAHORE_TZ))
    ).all()
    
    for challenge in expired_challenges:
        challenge.status = 'expired'
        challenged_team.forfeit_count += 1
        # Update ladder
```

### 2. Match Deadlines (10 days)

**Location**: `check_match_deadlines()` function

**Behavior**:
- Automatically forfeits matches that exceed 10-day deadline
- Determines forfeit based on which team proposed venue
- If neither team proposed, both teams get forfeited

**Code Flow**:
```python
def check_match_deadlines():
    now = datetime.now(LAHORE_TZ)
    overdue_matches = Match.query.filter(
        (Match.status == 'scheduled') &
        (Match.match_deadline.isnot(None)) &
        (Match.match_deadline < now)
    ).all()
```

### 3. Score Deadlines (5 hours)

**Location**: `check_score_deadlines()` function

**Behavior**:
- Automatically forfeits matches where scores weren't entered within 5 hours
- Determines forfeit based on which team entered the score
- If neither team entered score, both teams get forfeited

**Code Flow**:
```python
def check_score_deadlines():
    now = datetime.now(LAHORE_TZ)
    overdue_scores = Match.query.filter(
        (Match.status == 'played') &
        (Match.score_deadline.isnot(None)) &
        (Match.score_deadline < now) &
        (Match.score_approved.is_(None))
    ).all()
```

### 4. Forfeit Demotions (2 forfeits)

**Location**: `check_forfeit_demotions()` function

**Behavior**:
- Automatically demotes teams with 2 or more forfeits
- Demotion hierarchy: Platinum → Gold → Silver → Bronze
- Resets forfeit count after demotion
- Updates team rank to bottom of new tier

**Code Flow**:
```python
def check_forfeit_demotions():
    teams_to_demote = User.query.filter(
        (User.forfeit_count >= 2) &
        (User.status == 'active') &
        (User.is_admin == False)
    ).all()
```

### 5. Date Validation (10-day window)

**Location**: `validate_proposed_date()` function

**Behavior**:
- Prevents proposing dates that exceed 10 days from match creation
- Returns True/False for validation

**Code Flow**:
```python
def validate_proposed_date(proposed_date):
    now = datetime.now(LAHORE_TZ)
    max_date = now + timedelta(days=10)
    return proposed_date <= max_date
```

## UI Updates

### Dashboard Template

- Updated time limits in the rules reference section
- Shows current forfeit count for teams
- Displays deadline information for active matches

### Matches Template

- Added deadline display for scheduled matches
- Added score deadline display for played matches
- Visual indicators for expired deadlines (red pulsing animation)

### CSS Styling

Added styles for deadline display:
```css
.deadline {
    font-weight: 600;
    color: #667eea;
}

.deadline.expired {
    color: #e53e3e;
    animation: pulse 2s infinite;
}
```

## Automatic Execution

The time limit checks are automatically executed when users visit the dashboard:

```python
@app.route('/dashboard')
def dashboard():
    # Run time limit checks
    expired_challenges = check_challenge_expiration()
    overdue_matches = check_match_deadlines()
    overdue_scores = check_score_deadlines()
    demoted_teams = check_forfeit_demotions()
```

## Database Migration

A migration script (`migrate_time_limits.py`) was created to:

1. Add new columns to existing databases
2. Update existing matches with appropriate deadlines
3. Handle both scheduled and played matches

## Testing

A comprehensive test suite (`test_time_limits.py`) verifies:

1. Database schema integrity
2. Time limit function execution
3. Date validation logic
4. Forfeit processing

## Usage Examples

### Creating a New Match

When a challenge is accepted, a match is created with a 10-day deadline:

```python
new_match = Match(
    team1_id=challenge.challenging_team_id,
    team2_id=challenge.challenged_team_id,
    status='scheduled',
    match_deadline=datetime.now(LAHORE_TZ) + timedelta(days=10)
)
```

### Entering a Score

When a score is entered, a 5-hour deadline is set:

```python
match.score_deadline = datetime.now(LAHORE_TZ) + timedelta(hours=5)
```

### Proposing a Venue

Date validation prevents proposing dates beyond 10 days:

```python
if not validate_proposed_date(date):
    flash('Proposed date cannot exceed 10 days from match creation.', 'error')
```

## Monitoring and Maintenance

### Regular Checks

The system automatically checks for:
- Expired challenges (every dashboard visit)
- Overdue matches (every dashboard visit)
- Overdue scores (every dashboard visit)
- Teams eligible for demotion (every dashboard visit)

### Manual Override

Administrators can manually:
- Force complete matches
- Reset match status
- Adjust forfeit counts
- Override demotions

## Future Enhancements

Potential improvements:
1. Email notifications for approaching deadlines
2. Automated reminders for pending actions
3. Configurable time limits per tier
4. Detailed forfeit tracking and reporting
5. Appeal system for forfeits

## Troubleshooting

### Common Issues

1. **Deadlines not showing**: Ensure database migration was run
2. **Forfeits not counting**: Check that time limit functions are being called
3. **Demotions not happening**: Verify forfeit count is >= 2

### Debug Commands

```bash
# Run migration
python3 migrate_time_limits.py

# Test functionality
python3 test_time_limits.py

# Check database schema
python3 -c "from app import app, db, Match; print([c.name for c in Match.__table__.columns])"
```

## Conclusion

The time limits implementation ensures fair play and timely match completion while providing clear consequences for non-compliance. The system is automated, transparent, and maintains the competitive integrity of the league. 