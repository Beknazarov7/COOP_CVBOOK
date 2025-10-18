# 🚀 Deploy CV-Book on Render - Quick Guide

## Your Repository is Ready!

**GitHub:** https://github.com/MustafoAfzunov/CV-Book-For-UCA-Students  
**Branch:** main  
**Status:** ✅ All changes pushed

---

## Step-by-Step Deployment

### 1. Go to Render
Visit: https://render.com/  
Sign in with your GitHub account

### 2. Create New Web Service
- Click **"New +"** button in top right
- Select **"Web Service"**

### 3. Connect Repository
- Click **"Connect GitHub"** (if not already connected)
- Find and select: **MustafoAfzunov/CV-Book-For-UCA-Students**
- Click **"Connect"**

### 4. Configure Your Service

**Basic Settings:**
- **Name:** `cvbook` (or your preferred name)
- **Region:** Oregon (US West) or closest to your users
- **Branch:** `main`
- **Root Directory:** (leave blank)
- **Environment:** **Docker** ⚠️ IMPORTANT!
- **Dockerfile Path:** `./Dockerfile` (auto-detected)

**Instance Type:**
- Select: **Free** (or Starter if you need more resources)

### 5. Environment Variables (Click "Advanced")

Add these environment variables:

**Required:**
```
SECRET_KEY = <click "Generate" or paste your own>
DEBUG = False
ALLOWED_HOSTS = .onrender.com
```

**To generate SECRET_KEY locally:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Optional (for production database):**
```
DATABASE_URL = <your-postgres-connection-string>
```

### 6. Health Check Configuration

- **Health Check Path:** `/ping/`
- **Health Check Enabled:** Yes

### 7. Deploy!

- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes first time)
- Render will:
  - Clone your repository
  - Build Docker image
  - Run migrations
  - Start your app

---

## After Deployment

### Get Your URL
After deployment completes, you'll get a URL like:
```
https://cvbook-xyz123.onrender.com
```

### Update ALLOWED_HOSTS
1. Copy your Render URL
2. Go to Environment tab in Render dashboard
3. Update ALLOWED_HOSTS to include your URL:
   ```
   ALLOWED_HOSTS = cvbook-xyz123.onrender.com,.onrender.com
   ```
4. Save changes (app will auto-redeploy)

### Test Your Deployment

Visit these URLs:

1. **Main Page:**
   ```
   https://your-app.onrender.com/
   ```
   Should show: ✅ Login page

2. **Health Check:**
   ```
   https://your-app.onrender.com/ping/
   ```
   Should return: ✅ "OK" or JSON

3. **Admin Panel:**
   ```
   https://your-app.onrender.com/admin/
   ```
   Should show: ✅ Django admin login

4. **CV Cards:**
   ```
   https://your-app.onrender.com/cv-cards/
   ```
   Should show: ✅ CV cards page (after login)

---

## Common Issues & Solutions

### Issue: "Build Failed"
**Solution:**
- Check build logs in Render dashboard
- Verify Dockerfile syntax
- Ensure requirements.txt has all dependencies

### Issue: "Application Error" or 502
**Solution:**
- Check application logs in Render
- Verify SECRET_KEY is set
- Verify ALLOWED_HOSTS includes your Render domain
- Check DATABASE_URL if using PostgreSQL

### Issue: Static Files Not Loading
**Solution:**
- Ensure `collectstatic` runs in Dockerfile
- Check WhiteNoise is in MIDDLEWARE (already configured)
- Verify STATIC_ROOT is set (already configured)

### Issue: Database Errors
**Solution:**
- For SQLite: It's included in Docker, should work
- For PostgreSQL: 
  - Add PostgreSQL database in Render
  - Set DATABASE_URL environment variable
  - Redeploy

---

## Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (enough for one app)
- ✅ Auto-sleeps after 15 min inactivity
- ✅ 512 MB RAM
- ✅ Shared CPU
- ⚠️ First request after sleep takes ~30 seconds

**Upgrading:**
- Starter plan: $7/month
- No sleep, more resources

---

## Monitoring Your App

### View Logs:
1. Go to your service in Render dashboard
2. Click "Logs" tab
3. See real-time application logs

### Check Health:
1. Go to "Events" tab
2. See deployment history
3. Check health check status

### Metrics:
1. Go to "Metrics" tab
2. See CPU, memory usage
3. Monitor request rates

---

## Updating Your App

### After Making Code Changes:

```bash
cd /home/user/UCA/CV-Book-for-Cooperative-Department

# Make your changes, then:
git add .
git commit -m "Your change description"
git push origin main
```

**Render will auto-deploy** when you push to main branch!

---

## Custom Domain (Optional)

### Add Your Own Domain:

1. In Render dashboard → Settings
2. Scroll to "Custom Domain"
3. Click "Add Custom Domain"
4. Enter your domain (e.g., cvbook.yourdomain.com)
5. Update your DNS with CNAME record
6. Update ALLOWED_HOSTS environment variable

---

## Database Backup (Important!)

### For SQLite:
- Data is lost when container restarts
- ⚠️ Not recommended for production
- Use PostgreSQL for production!

### Add PostgreSQL:
1. In Render dashboard → New +
2. Select "PostgreSQL"
3. Name: cvbook-db
4. Plan: Free
5. Create database
6. Copy connection string
7. Add to your web service as DATABASE_URL
8. Redeploy

---

## Quick Reference

### Your Repository:
```
https://github.com/MustafoAfzunov/CV-Book-For-UCA-Students
```

### Render Dashboard:
```
https://dashboard.render.com
```

### Health Check Endpoint:
```
/ping/
```

### Files in Your Repo:
- ✅ Dockerfile - Container config
- ✅ .dockerignore - Build optimization
- ✅ render.yaml - Deployment blueprint
- ✅ requirements.txt - Python dependencies
- ✅ start.sh - Startup script (for Gunicorn)

---

## Summary

✅ **Code pushed to GitHub**  
✅ **Docker configuration included**  
✅ **Health checks configured**  
✅ **Root URL shows login page**  
✅ **Ready for Render deployment**

**Next:** Go to render.com and deploy! 🎉

---

*Deployment guide created: October 18, 2025*  
*Your app is production-ready!*

