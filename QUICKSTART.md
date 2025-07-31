# 🚀 CPL Quick Start Guide

Get the Chiniot Padel League running in minutes!

## ⚡ Super Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Download and extract the CPL files
# Then run the deployment script
./deploy.sh
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python3 app.py
```

### Option 3: Docker Setup
```bash
# Build and run with Docker
docker-compose up --build
```

## 🎯 What You'll Get

After running the setup, you'll have:

- ✅ **Web Application** running at `http://localhost:5000`
- ✅ **Database** initialized with tables
- ✅ **Admin Panel** for managing the league
- ✅ **Tier System** with Platinum, Gold, Silver, Bronze teams
- ✅ **Challenge System** with advanced rules
- ✅ **Live Rankings** with real-time updates

## 👥 First Steps

### 1. Create Admin Account
1. Go to `http://localhost:5000/register`
2. Register a new team
3. Manually set `is_admin=True` in the database for that user
4. Log in with the admin account

### 2. Add Teams (Optional)
```bash
# Add 50 dummy teams for testing
python3 add_dummy_teams.py
```

### 3. Test the System
```bash
# Run tests to verify everything works
python3 test_tier_system.py
python3 test_consecutive_rule_fixed.py
```

## 🎮 Using the Application

### For Players
1. **Register**: Create a team account
2. **Challenge**: Challenge teams ranked higher than you
3. **Play Matches**: Complete matches and update rankings
4. **View Rankings**: Check your position and tier

### For Administrators
1. **Login**: Use your admin account
2. **Manage Teams**: Edit, freeze, or delete teams
3. **Manage Challenges**: Force accept/reject challenges
4. **Manage Matches**: Control match outcomes and status

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Database
- **Default**: SQLite (good for development)
- **Production**: PostgreSQL or MySQL

## 🐳 Docker Commands

```bash
# Start the application
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild and start
docker-compose up --build
```

## 🧪 Testing

```bash
# Test tier system
python3 test_tier_system.py

# Test challenge rules
python3 test_consecutive_rule_fixed.py

# Add dummy data
python3 add_dummy_teams.py

# Clear all data
python3 clear_data.py
```

## 🆘 Troubleshooting

### Common Issues

**Port 5000 already in use:**
```bash
# Change port in app.py or use different port
python3 app.py --port 5001
```

**Database errors:**
```bash
# Clear and reinitialize database
python3 clear_data.py
python3 app.py
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x deploy.sh
```

**Docker issues:**
```bash
# Clean up Docker
docker-compose down -v
docker system prune -f
docker-compose up --build
```

## 📞 Support

- 📖 **Full Documentation**: See `README.md`
- 🐛 **Issues**: Check the troubleshooting section
- 🧪 **Tests**: Run test scripts to verify functionality

## 🎯 Next Steps

1. **Customize**: Modify team names, rules, or styling
2. **Deploy**: Set up for production use
3. **Scale**: Add more features or integrate with other systems

---

**🏆 Ready to play? Start your competitive padel tennis league today!** 