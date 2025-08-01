# 🚀 Supabase + Vercel Integration Guide

## ✅ **Why Supabase is Perfect for Vercel:**

### **Benefits:**
- ✅ **PostgreSQL Database** - Full SQL database
- ✅ **Real-time subscriptions** - Live data updates
- ✅ **Authentication** - Built-in auth system
- ✅ **Row Level Security** - Advanced security
- ✅ **Auto-generated APIs** - REST and GraphQL
- ✅ **Free tier** - Generous free plan
- ✅ **Vercel integration** - Works seamlessly

## 🎯 **Setup Steps:**

### **Step 1: Create Supabase Project**
1. **Go to [supabase.com](https://supabase.com)**
2. **Sign up/Login**
3. **Click "New Project"**
4. **Choose organization**
5. **Enter project details:**
   - **Name:** `cpl-padel-league`
   - **Database Password:** (create a strong password)
   - **Region:** Choose closest to you
6. **Click "Create new project"**

### **Step 2: Get Supabase Credentials**
1. **Go to Settings → API**
2. **Copy these values:**
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_ANON_KEY)

### **Step 3: Create Database Tables**
1. **Go to SQL Editor**
2. **Run this SQL to create tables:**

```sql
-- Create teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert admin user
INSERT INTO teams (team_name, password, is_admin, status) 
VALUES ('admin', 'admin', TRUE, 'active');

-- Create matches table
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    team1_id INTEGER REFERENCES teams(id),
    team2_id INTEGER REFERENCES teams(id),
    winner_id INTEGER REFERENCES teams(id),
    score VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create challenges table
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    challenger_id INTEGER REFERENCES teams(id),
    challenged_id INTEGER REFERENCES teams(id),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Step 4: Set Environment Variables in Vercel**
1. **Go to your Vercel project dashboard**
2. **Go to Settings → Environment Variables**
3. **Add these variables:**
   - **SUPABASE_URL** = Your Supabase project URL
   - **SUPABASE_ANON_KEY** = Your Supabase anon key
   - **SECRET_KEY** = A secure random string

### **Step 5: Deploy to Vercel**
1. **Push your code to GitHub**
2. **Vercel will automatically deploy**
3. **Check the deployment logs**

## 🎉 **Features:**

### **✅ Working with Supabase:**
- **Persistent data** - Data survives serverless restarts
- **Real-time updates** - Live data changes
- **Scalable** - Handles growth
- **Secure** - Row Level Security
- **Fast** - Optimized queries

### **✅ Fallback System:**
- **In-memory fallback** - Works if Supabase is down
- **Graceful degradation** - App still functions
- **Error handling** - Catches connection issues

## 🔧 **Environment Variables:**

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SECRET_KEY=your-secret-key-here
```

## 🚀 **Deploy:**

```bash
git add .
git commit -m "Add Supabase integration"
git push origin main
vercel --prod
```

## 📱 **Admin Login:**
- **Team Name:** `admin`
- **Password:** `admin`

**Your app will now have a real database with Supabase!** 🎉 