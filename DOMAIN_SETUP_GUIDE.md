# 🌐 **Custom Domain Setup Guide**

## **Step 1: Purchase Domain from GoDaddy**

1. Visit [GoDaddy.com](https://www.godaddy.com)
2. Search for your desired domain (e.g., `cpalleague.com`)
3. Complete the purchase

## **Step 2: Configure Domain in Railway**

### **In Railway Dashboard:**
1. Go to your CPL project
2. Click on the "web" service
3. Go to "Settings" tab
4. Find "Custom Domains" section
5. Click "Add Domain"
6. Enter your domain (e.g., `cpalleague.com`)
7. Railway will provide you with DNS records

## **Step 3: Configure DNS in GoDaddy**

### **Option A: Root Domain (cpalleague.com)**
1. Log into GoDaddy account
2. Go to "My Domains" → "Manage" → "DNS"
3. Add these records:

```
Type: CNAME
Name: @ (or leave blank)
Value: web-production-2a510.up.railway.app
TTL: 600
```

### **Option B: Subdomain (app.cpalleague.com)**
1. In Railway: Add `app.cpalleague.com`
2. In GoDaddy DNS:
```
Type: CNAME
Name: app
Value: web-production-2a510.up.railway.app
TTL: 600
```

## **Step 4: SSL Certificate**

Railway will automatically provision an SSL certificate for your domain once DNS is configured correctly.

## **Step 5: Verify Setup**

1. **Wait 5-10 minutes** for DNS propagation
2. **Visit your domain** (e.g., `https://cpalleague.com`)
3. **Test admin login:**
   - Username: `Admin`
   - Password: `admin123`

## **🌐 Recommended Domain Names**

- `cpalleague.com`
- `chiniotpadel.com`
- `cpldashboard.com`
- `padelleague.com`
- `cpldubai.com`

## **💰 Estimated Costs**

- **Domain:** $10-15/year (GoDaddy)
- **Railway:** $5/month (current plan)
- **Total:** ~$75-85/year

## **✅ Benefits of Custom Domain**

1. **Professional appearance**
2. **Easy to remember**
3. **Brand recognition**
4. **SSL certificate included**
5. **Better for sharing with teams**

## **🔧 Troubleshooting**

### **If domain doesn't work:**
1. **Check DNS propagation** at [whatsmydns.net](https://www.whatsmydns.net)
2. **Verify CNAME record** in GoDaddy
3. **Check Railway domain status**
4. **Wait 24 hours** for full propagation

### **Common Issues:**
- **DNS not propagated** - Wait longer
- **Wrong CNAME value** - Use exact Railway URL
- **SSL certificate pending** - Wait 10-15 minutes

## **📞 Support**

If you encounter issues:
1. Check Railway logs
2. Verify DNS settings
3. Contact Railway support if needed 