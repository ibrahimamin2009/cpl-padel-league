# 🏓 CPL - Competitive Pickleball League

A comprehensive web application for managing competitive pickleball leagues with automatic time limits, forfeit handling, and tier-based rankings.

## ✨ Features

- **Team Management**: Register teams with player information
- **Challenge System**: Lower-ranked teams can challenge higher-ranked teams
- **Match Management**: Schedule, play, and score matches
- **Automatic Time Limits**: 
  - 24 hours to respond to challenges
  - 10 days to play accepted matches
  - 5 hours to enter scores after match time
- **Forfeit System**: Automatic demotion after 2 forfeits
- **Tier System**: Platinum, Gold, Silver, Bronze tiers
- **Real-time Rankings**: Live ladder updates
- **Admin Panel**: Complete administrative control
- **Lahore Timezone**: All times in Pakistan timezone

## 🚀 Quick Deploy (Free)

### Railway (Recommended - 5 minutes)
1. **Fork/Clone this repository**
2. **Go to [railway.app](https://railway.app)**
3. **Sign up with GitHub**
4. **Click "New Project" → "Deploy from GitHub repo"**
5. **Select this repository**
6. **Add PostgreSQL database**
7. **Set environment variables:**
   - `SECRET_KEY`: Generate a random string
   - `FLASK_ENV`: `production`
8. **Deploy!**

Your app will be live at: `https://your-app-name.railway.app`

### Alternative Free Options
- **Render**: 750 free hours/month
- **PythonAnywhere**: Python-focused hosting
- **Fly.io**: 3 free VMs

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd CPL

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python3 deploy.py

# Run the application
python3 app.py
```

### Environment Variables
Create a `.env` file:
```bash
SECRET_KEY=your-super-secret-key
FLASK_ENV=development
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📊 Database Schema

### Users (Teams)
- Team information (name, players, emails)
- Rank and tier
- Forfeit count
- Admin status

### Challenges
- Challenging and challenged teams
- Status (pending, accepted, rejected, expired)
- Expiration time (24 hours)

### Matches
- Team participants
- Venue and date coordination
- Score tracking
- Time limits (10 days to play, 5 hours to score)

## ⏰ Time Limits

All times are in **Lahore, Pakistan timezone**:

- **Challenge Response**: 24 hours
- **Match Play**: 10 days from acceptance
- **Score Entry**: 5 hours from match completion
- **Date Proposals**: Must be within 10-day window

## 🏆 Tier System

- **Platinum**: Ranks 1-10
- **Gold**: Ranks 11-30
- **Silver**: Ranks 31-60
- **Bronze**: Ranks 61+

## 🔧 Configuration

### Production Deployment
Set these environment variables:
```bash
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
DATABASE_URL=postgresql://...
```

### Email Configuration
```bash
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

## 📱 Usage

### For Players
1. **Register** your team
2. **Challenge** higher-ranked teams
3. **Schedule** matches within time limits
4. **Enter scores** after playing
5. **Monitor** your ranking

### For Admins
1. **Login** as Admin (password: admin123)
2. **Manage** team registrations
3. **Monitor** challenges and matches
4. **Export** league data
5. **Configure** tiers and settings

## 🎯 API Endpoints

- `GET /api/ranking` - Live rankings data
- `POST /challenge` - Send challenges
- `GET /matches` - View all matches
- `GET /dashboard` - Main dashboard

## 🔒 Security

- Password hashing with Werkzeug
- Session management
- Admin-only routes protected
- CSRF protection
- Input validation

## 📈 Analytics

- Team statistics
- Match completion rates
- Tier distribution
- Forfeit tracking
- Export functionality

## 🆘 Support

### Common Issues
1. **Timezone issues**: All times are in Lahore timezone
2. **Database errors**: Run `python3 deploy.py` to set up
3. **Email not working**: Check SMTP settings

### Getting Help
- Check the logs for error messages
- Verify environment variables
- Test locally before deploying

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**🏓 Ready to start your pickleball league? Deploy now and get playing!** 