# 📧 Email Notifications Setup Guide - CPL

## Overview

The CPL system now includes comprehensive email notifications to keep teams informed about:
- New challenges received
- Challenge responses (accepted/rejected)
- Venue proposals
- Match deadline reminders
- Score entry reminders

## 🔧 Email Configuration

### 1. **Gmail Setup (Recommended)**

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. This is required to generate an App Password

#### Step 2: Generate App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "App passwords" (under 2-Step Verification)
3. Select "Mail" and "Other (Custom name)"
4. Name it "CPL Notifications"
5. Copy the generated 16-character password

#### Step 3: Set Environment Variables
```bash
# For development (.env file)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password

# For production (Railway/Render)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
```

### 2. **Alternative Email Providers**

#### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

#### Yahoo
```bash
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

#### Custom SMTP Server
```bash
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-password
```

## 🚀 Deployment Setup

### Railway Deployment
1. **Set Environment Variables:**
   - Go to your Railway project dashboard
   - Click on your app service
   - Go to "Variables" tab
   - Add these variables:
     ```
     MAIL_USERNAME=your-email@gmail.com
     MAIL_PASSWORD=your-app-password
     ```

### Render Deployment
1. **Set Environment Variables:**
   - Go to your Render dashboard
   - Click on your web service
   - Go to "Environment" tab
   - Add these variables:
     ```
     MAIL_USERNAME=your-email@gmail.com
     MAIL_PASSWORD=your-app-password
     ```

### Local Development
1. **Create .env file:**
   ```bash
   SECRET_KEY=your-secret-key
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

## 📧 Email Notifications Types

### 1. **Challenge Notifications**
- **Triggered when:** Team sends a challenge
- **Sent to:** Challenged team (both players)
- **Content:** Challenge details, expiration time

### 2. **Challenge Response Notifications**
- **Triggered when:** Team accepts/rejects challenge
- **Sent to:** Challenging team (both players)
- **Content:** Response status, match details (if accepted)

### 3. **Venue Proposal Notifications**
- **Triggered when:** Team proposes venue/time
- **Sent to:** Opponent team (both players)
- **Content:** Proposed venue, date, approval request

### 4. **Match Reminder Notifications**
- **Triggered when:** Match deadline approaches (2 days before)
- **Sent to:** Both teams (all players)
- **Content:** Match details, deadline warning

### 5. **Score Entry Reminders**
- **Triggered when:** Score deadline approaches (2 hours before)
- **Sent to:** Both teams (all players)
- **Content:** Score entry deadline warning

## 🔄 Manual Reminder System

### Admin Dashboard
1. **Login as admin**
2. **Go to Admin Dashboard**
3. **Click "Send Email Reminders" button**
4. **System will send reminders to:**
   - Teams with upcoming match deadlines
   - Teams with pending score entries

### Automated Reminders (Future)
For production deployment, consider setting up a cron job:
```bash
# Run every hour
0 * * * * curl -X POST https://your-app.railway.app/admin/send-reminders
```

## 🧪 Testing Email Notifications

### 1. **Test Challenge Notifications**
1. Register two test teams
2. Send a challenge from one team to another
3. Check email inboxes for challenge notification

### 2. **Test Response Notifications**
1. Accept/reject the challenge
2. Check challenging team's email for response notification

### 3. **Test Manual Reminders**
1. Create a match with deadline approaching
2. Login as admin
3. Click "Send Email Reminders"
4. Check team email inboxes

## ⚠️ Troubleshooting

### Common Issues

#### 1. **"Email sending failed" Error**
- **Cause:** Invalid email credentials
- **Solution:** 
  - Verify Gmail app password is correct
  - Check 2FA is enabled
  - Ensure environment variables are set

#### 2. **Emails Not Received**
- **Cause:** Email in spam folder
- **Solution:**
  - Check spam/junk folder
  - Add sender email to contacts
  - Whitelist the email address

#### 3. **Authentication Error**
- **Cause:** Gmail security settings
- **Solution:**
  - Enable "Less secure app access" (not recommended)
  - Use App Password instead
  - Check Gmail account security settings

#### 4. **Production Email Issues**
- **Cause:** Environment variables not set
- **Solution:**
  - Verify Railway/Render environment variables
  - Check deployment logs for errors
  - Test with admin reminder function

### Debug Mode
To enable email debugging, add to your app:
```python
app.config['MAIL_DEBUG'] = True
```

## 📊 Email Analytics

### Monitor Email Success
- Check application logs for email errors
- Monitor bounce rates
- Track email delivery success

### Email Templates
All email templates are in the `send_*_notification` functions in `app.py`:
- `send_challenge_notification()`
- `send_challenge_response_notification()`
- `send_venue_proposal_notification()`
- `send_match_reminder_notification()`
- `send_score_reminder_notification()`

## 🔒 Security Considerations

### Email Security
- Use App Passwords, not regular passwords
- Enable 2FA on email accounts
- Monitor for suspicious activity
- Use environment variables for credentials

### Privacy
- Email addresses are stored in database
- Only used for CPL notifications
- No third-party email services
- Emails contain only necessary information

## 📞 Support

If you encounter email issues:
1. Check the troubleshooting section above
2. Verify environment variables are set correctly
3. Test with admin reminder function
4. Check application logs for specific error messages

---

**Note:** Email notifications are now fully integrated into the CPL system. Teams will automatically receive notifications for all important events, helping to keep the league running smoothly! 