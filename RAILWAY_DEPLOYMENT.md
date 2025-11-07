# 🚂 Railway Deployment Guide - CVBook Project

## ✅ Configuration Files Created

I've created all necessary Railway configuration files for your CVBook project:

### Files Added:
1. ✅ `nixpacks.toml` - Railway/Nixpacks build configuration
2. ✅ `railway.json` - Railway deployment settings
3. ✅ `Procfile` - Process definition (fallback)
4. ✅ `runtime.txt` - Python version specification

---

## 📋 Deployment Steps

### Step 1: Commit Configuration Files

```bash
cd /home/user/UCA/CV-Book-for-Cooperative-Department

# Add new configuration files
git add nixpacks.toml railway.json Procfile runtime.txt

# Also add the CORS changes from earlier
git add CVBOOK/settings.py requirements.txt

# Commit all changes
git commit -m "Add Railway deployment configuration and CORS support

- Added nixpacks.toml for Railway build configuration
- Added railway.json for deployment settings
- Added Procfile for process definition
- Added runtime.txt for Python version
- Enabled CORS for production integration
- Added django-cors-headers to requirements"
```

### Step 2: Set Environment Variables in Railway

Go to your **Railway Dashboard** → **CVBook Project** → **Variables** tab

Add these environment variables:

```bash
# Basic Django Settings
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-a-new-secret-key>

# Allowed Hosts (CRITICAL)
ALLOWED_HOSTS=ucagraduatecvbook.org,.railway.app,.up.railway.app,healthcheck.railway.app

# CORS Configuration (for integration with main site)
CORS_ALLOWED_ORIGINS=https://ucacoop.org,https://ucagraduatecvbook.org
CSRF_TRUSTED_ORIGINS=https://ucagraduatecvbook.org,https://ucacoop.org,https://*.railway.app

# Database (provided automatically by Railway if you add PostgreSQL)
# DATABASE_URL=<automatically-set-by-railway>

# Email Settings (if needed)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Generate a new SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Add PostgreSQL Database (Recommended)

In Railway Dashboard:
1. Click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically set `DATABASE_URL` environment variable
3. Your Django app will use it automatically via `dj-database-url`

### Step 4: Push to Railway

```bash
# If you haven't connected to Railway yet:
# railway link

# Push your changes
git push railway main

# OR if using GitHub/GitLab:
git push origin main
# Railway will auto-deploy from your connected repo
```

### Step 5: Monitor Deployment

1. Go to Railway Dashboard
2. Click on your CVBook project
3. Go to **"Deployments"** tab
4. Watch the build logs
5. Wait for status to show **"Active"**

### Step 6: Verify Deployment

```bash
# Test the deployed site
curl https://ucagraduatecvbook.org

# Test the API
curl https://ucagraduatecvbook.org/cv/api/list/

# Run full integration test
cd /home/user/UCA
./test-production-integration.sh
```

---

## 🔧 Configuration Files Explained

### 1. nixpacks.toml

```toml
[phases.setup]
nixPkgs = ["python310", "postgresql"]

[phases.install]
cmds = [
    "pip install --upgrade pip",
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput"
]

[start]
cmd = "python manage.py migrate && gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT --workers 4"
```

**What it does:**
- Sets up Python 3.10 and PostgreSQL
- Installs dependencies from requirements.txt
- Collects static files during build
- Runs migrations and starts Gunicorn on deployment

### 2. railway.json

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT --workers 4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**What it does:**
- Tells Railway to use Nixpacks builder
- Defines build and deployment commands
- Sets restart policy for automatic recovery

### 3. Procfile

```
web: python manage.py migrate && gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT --workers 4
```

**What it does:**
- Fallback process definition
- Ensures app starts correctly if Railway.json isn't read

### 4. runtime.txt

```
python-3.10.12
```

**What it does:**
- Specifies exact Python version to use

---

## 🔍 Common Railway Deployment Issues

### Issue 1: Build Fails - "Module not found"

**Solution:** Make sure all packages are in `requirements.txt`

```bash
# Verify requirements
cat requirements.txt

# Should include:
# - Django
# - gunicorn
# - psycopg2-binary
# - django-cors-headers
# - djangorestframework
# - whitenoise
```

### Issue 2: App Crashes - "relation does not exist"

**Solution:** Migrations not running

Check Railway logs and ensure the start command includes:
```bash
python manage.py migrate && gunicorn...
```

### Issue 3: Static Files Not Loading

**Solution:** Ensure `collectstatic` runs during build

In `railway.json`:
```json
"buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
```

### Issue 4: CORS Errors

**Solution:** Set environment variables in Railway dashboard

```bash
CORS_ALLOWED_ORIGINS=https://ucacoop.org,https://ucagraduatecvbook.org
CSRF_TRUSTED_ORIGINS=https://ucagraduatecvbook.org,https://ucacoop.org,https://*.railway.app
```

### Issue 5: Port Binding Error

**Solution:** Use Railway's `$PORT` environment variable

In start command:
```bash
gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT
```

---

## 📊 Deployment Checklist

Before deploying:

- [ ] All configuration files committed
- [ ] `requirements.txt` is up to date
- [ ] `ALLOWED_HOSTS` includes Railway domains
- [ ] `SECRET_KEY` is set in Railway (not in code)
- [ ] `DEBUG=False` in Railway environment variables
- [ ] CORS settings configured
- [ ] Database added (PostgreSQL recommended)
- [ ] Email settings configured (if needed)

After deploying:

- [ ] Build completed successfully
- [ ] Deployment shows "Active" status
- [ ] Website accessible at your domain
- [ ] API endpoints working
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] No errors in Railway logs

---

## 🚀 Quick Deploy Commands

```bash
# Full deployment workflow
cd /home/user/UCA/CV-Book-for-Cooperative-Department

# 1. Add files
git add nixpacks.toml railway.json Procfile runtime.txt CVBOOK/settings.py requirements.txt

# 2. Commit
git commit -m "Add Railway deployment configuration"

# 3. Push
git push railway main

# 4. Monitor (in Railway dashboard or CLI)
railway logs

# 5. Test
curl https://ucagraduatecvbook.org/cv/api/list/
```

---

## 📝 Environment Variables Template

Copy this template for Railway environment variables:

```bash
# Django Core
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=django-insecure-CHANGE-THIS-TO-RANDOM-KEY

# Hosts
ALLOWED_HOSTS=ucagraduatecvbook.org,.railway.app,.up.railway.app,healthcheck.railway.app

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://ucacoop.org,https://ucagraduatecvbook.org
CSRF_TRUSTED_ORIGINS=https://ucagraduatecvbook.org,https://ucacoop.org,https://*.railway.app

# Database (set automatically by Railway PostgreSQL)
# DATABASE_URL=postgresql://user:password@host:port/database

# Email (optional)
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Optional: API Key for secure communication
# CVBOOK_API_KEY=
```

---

## 🔐 Security Checklist

- [ ] `SECRET_KEY` is unique and not in git
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] CORS origins restricted to known domains
- [ ] CSRF trusted origins configured
- [ ] Database credentials not in code
- [ ] Email credentials in environment variables
- [ ] SSL/HTTPS enabled (automatic on Railway)

---

## 📞 Support & Troubleshooting

### View Railway Logs

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs
```

### Common Commands

```bash
# View recent logs
railway logs --limit 100

# Follow logs in real-time
railway logs --follow

# Open Railway dashboard
railway open

# Run commands in Railway environment
railway run python manage.py shell
```

### Check Deployment Status

```bash
# Test basic connectivity
curl -I https://ucagraduatecvbook.org

# Test API
curl https://ucagraduatecvbook.org/cv/api/list/

# Test admin panel
curl -I https://ucagraduatecvbook.org/admin/

# Run full integration test
cd /home/user/UCA
./test-production-integration.sh
```

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Railway shows "Active" deployment status
2. ✅ Website accessible at https://ucagraduatecvbook.org
3. ✅ API returns data: `curl https://ucagraduatecvbook.org/cv/api/list/`
4. ✅ Admin panel redirects properly: `/admin/`
5. ✅ CV form loads without 500 error
6. ✅ CV gallery displays: `/cv-cards/`
7. ✅ No errors in Railway logs
8. ✅ Integration test passes: `./test-production-integration.sh`

---

## 🎯 Next Steps

After successful deployment:

1. **Test the integration:**
   ```bash
   ./test-production-integration.sh
   ```

2. **Deploy main website with CVBook integration:**
   Follow the steps in `README_DEPLOYMENT_NOW.md`

3. **Set environment variables in main website:**
   ```
   CVBOOK_API_URL=https://ucagraduatecvbook.org
   CVBOOK_PUBLIC_URL=https://ucagraduatecvbook.org
   ```

4. **Test end-to-end integration:**
   - Student CV submission
   - Admin CV management
   - Public CV gallery

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Nixpacks Documentation](https://nixpacks.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**Ready to deploy? Follow Step 1 above!** 🚀




