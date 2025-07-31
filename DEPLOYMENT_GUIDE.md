# 🚀 CPL Padel League Deployment Guide - Free Options

## 🆓 **Railway (Recommended - Easiest)**

### Step 1: Prepare Your Code
✅ Already done! Your app is ready with:
- `Procfile` - tells Railway how to run your app
- `requirements.txt` - lists Python dependencies
- `railway.json` - Railway configuration
- `config.py` - handles production settings

### Step 2: Deploy to Railway
1. **Go to [railway.app](https://railway.app)**
2. **Sign up** with your GitHub account
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select your CPL repository**
5. **Add PostgreSQL database:**
   - Click "New" → "Database" → "PostgreSQL"
6. **Set environment variables:**
   - `SECRET_KEY`: Generate a random string
   - `DATABASE_URL`: Railway will set this automatically
   - `FLASK_ENV`: Set to `production`

### Step 3: Get Your URL
- Railway will give you a URL like: `https://your-app-name.railway.app`
- Share this URL with your pickleball league!

---

## 🆓 **Render (Alternative - More Free Hours)**

### Step 1: Deploy to Render
1. **Go to [render.com](https://render.com)**
2. **Sign up** with GitHub
3. **Click "New"** → **"Web Service"**
4. **Connect your GitHub repo**
5. **Configure:**
   - **Name**: `cpl-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. **Add PostgreSQL database:**
   - Click "New" → "PostgreSQL"
   - Connect it to your web service

### Step 2: Environment Variables
Set these in Render dashboard:
- `SECRET_KEY`: Random string
- `DATABASE_URL`: Render will set this
- `FLASK_ENV`: `production`

---

## 🆓 **PythonAnywhere (Python-focused)**

### Step 1: Sign Up
1. **Go to [pythonanywhere.com](https://pythonanywhere.com)**
2. **Create free account**
3. **Upload your code** or connect GitHub

### Step 2: Configure
1. **Create new web app**
2. **Choose Flask framework**
3. **Set up virtual environment**
4. **Install requirements**: `pip install -r requirements.txt`
5. **Configure WSGI file**

---

## 🔧 **Environment Variables to Set**

```bash
# Required for all platforms
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Database (set automatically by platform)
DATABASE_URL=postgresql://...

# Optional: Email settings
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 🎯 **Quick Start: Railway (5 minutes)**

1. **Push your code to GitHub** (if not already done)
2. **Go to [railway.app](https://railway.app)**
3. **Sign up with GitHub**
4. **Click "New Project"** → **"Deploy from GitHub repo"**
5. **Select your CPL repo**
6. **Add PostgreSQL database**
7. **Set environment variables**
8. **Deploy!**

Your app will be live at: `https://your-app-name.railway.app`

---

## 📱 **After Deployment**

### Test Your App
- ✅ Login functionality
- ✅ Team registration
- ✅ Challenge system
- ✅ Match management
- ✅ Rankings

### Share with Your League
- Send the URL to all players
- Create admin accounts
- Set up initial teams

### Monitor Usage
- Railway: Check dashboard for usage
- Render: Monitor in dashboard
- PythonAnywhere: Check usage limits

---

## 💡 **Tips for Free Tiers**

### Railway
- **500 hours/month** = ~16 hours/day
- Perfect for a league with regular usage
- Sleeps after 5 minutes of inactivity

### Render
- **750 hours/month** = 24/7 usage possible
- More generous than Railway
- Great for active leagues

### PythonAnywhere
- **CPU time limits** on free tier
- Good for smaller leagues
- Web-based management

---

## 🆘 **Need Help?**

- **Railway**: Excellent documentation and Discord
- **Render**: Good documentation and support
- **PythonAnywhere**: Python-focused community

**Your CPL app is ready to deploy! 🏓** 