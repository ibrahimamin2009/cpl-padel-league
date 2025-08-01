# 🚀 Render Deployment Guide

## Why Render?
- ✅ **More reliable** than Railway
- ✅ **Better error logs** - easier to debug
- ✅ **Free PostgreSQL** database included
- ✅ **Automatic deployments** from GitHub
- ✅ **Better performance**

## 📋 Prerequisites
1. **GitHub account** with your code pushed
2. **Render account** (free at render.com)
3. **Gmail account** for email notifications

## 🛠️ Step-by-Step Deployment

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub account
- Verify your email

### 2. Connect Your Repository
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Select your CPL repository

### 3. Configure the Service
- **Name**: `cpl-padel-league`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free

### 4. Set Environment Variables
Click "Environment" tab and add:

```
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
RENDER_ENVIRONMENT=production
```

### 5. Add PostgreSQL Database
- Go to "Databases" in Render dashboard
- Click "New +" → "PostgreSQL"
- Name: `cpl-database`
- Plan: Free
- Copy the **Internal Database URL**

### 6. Link Database to App
- Go back to your web service
- In "Environment" tab, add:
```
DATABASE_URL=your-postgresql-internal-url
```

### 7. Deploy
- Click "Create Web Service"
- Render will automatically deploy your app
- Wait for build to complete (2-3 minutes)

## 🔧 Post-Deployment Setup

### 1. Initialize Database
Once deployed, visit your app URL and it will automatically:
- Create all database tables
- Create admin account (admin/admin)

### 2. Test Admin Login
- Go to your app URL
- Login with:
  - **Team Name**: `admin`
  - **Password**: `admin`

### 3. Configure Email (Optional)
If you want email notifications:
1. Enable 2FA on your Gmail
2. Generate App Password
3. Add to environment variables

## 🐛 Troubleshooting

### If App Won't Start
1. Check build logs in Render dashboard
2. Verify all environment variables are set
3. Ensure `requirements.txt` is correct

### If Database Issues
1. Check if PostgreSQL is connected
2. Verify `DATABASE_URL` is correct
3. Check if tables are created

### If Admin Login Fails
1. Check if admin account was created
2. Try accessing `/admin` directly
3. Check database logs

## 📞 Support
- Render has excellent documentation
- Better error messages than Railway
- Active community support

## 🎉 Benefits of Render
- **Reliable**: 99.9% uptime
- **Fast**: Global CDN
- **Secure**: HTTPS by default
- **Scalable**: Easy to upgrade
- **Free**: Generous free tier

Your app should work perfectly on Render! 🚀 