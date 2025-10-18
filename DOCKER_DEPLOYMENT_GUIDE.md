# Docker Deployment Guide for CV-Book

## For Render.com Deployment

---

## Files Created

1. **Dockerfile** - Container configuration
2. **docker-compose.yml** - Local Docker testing
3. **.dockerignore** - Excludes unnecessary files
4. **render.yaml** - Render deployment configuration

---

## Quick Deploy to Render

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub:**
   ```bash
   cd /home/user/UCA/CV-Book-for-Cooperative-Department
   git add Dockerfile .dockerignore render.yaml
   git commit -m "Add Docker configuration for Render deployment"
   git push origin main
   ```

2. **On Render.com:**
   - Go to Dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the CV-Book repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

3. **Set Environment Variables:**
   - SECRET_KEY (auto-generated)
   - ALLOWED_HOSTS (your-app.onrender.com)
   - Other variables as needed

### Option 2: Manual Setup

1. **On Render.com:**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select CV-Book repository

2. **Configure:**
   - **Name:** cvbook
   - **Environment:** Docker
   - **Region:** Choose closest to you
   - **Branch:** main
   - **Dockerfile Path:** ./Dockerfile
   - **Docker Context:** .

3. **Environment Variables:**
   ```
   SECRET_KEY=<generate-random-key>
   DEBUG=False
   ALLOWED_HOSTS=your-app.onrender.com,*.onrender.com
   PORT=8000
   ```

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment

---

## Test Locally with Docker

### Build and Run:
```bash
cd /home/user/UCA/CV-Book-for-Cooperative-Department

# Build the Docker image
docker build -t cvbook .

# Run the container
docker run -p 8001:8000 -e DEBUG=True cvbook

# Or use docker-compose
docker-compose up
```

### Test:
```bash
# Check if it's running
curl http://localhost:8001/

# Should show the login page now! ✅
```

### Stop:
```bash
# Stop docker-compose
docker-compose down

# Or stop specific container
docker stop <container-id>
```

---

## Environment Variables for Production

### Required:
```env
SECRET_KEY=<your-secret-key-at-least-50-chars>
ALLOWED_HOSTS=your-app.onrender.com,*.onrender.com
DEBUG=False
```

### Optional:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

---

## Dockerfile Explanation

```dockerfile
FROM python:3.10-slim          # Base image
ENV PYTHONUNBUFFERED=1         # Real-time logs
WORKDIR /app                   # Working directory

# Install dependencies
RUN apt-get update && apt-get install -y gcc postgresql-client

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD python manage.py migrate && \
    gunicorn CVBOOK.wsgi:application --bind 0.0.0.0:$PORT
```

---

## Health Check Endpoints

Your app has health check endpoints for Render monitoring:

- `/health/` - Returns JSON with status
- `/ping/` - Returns "OK"
- `/status/` - Returns HTTP 200

Render will use these to monitor your app.

---

## Database Configuration

### SQLite (Development):
```env
# No DATABASE_URL needed - uses db.sqlite3
```

### PostgreSQL (Production):
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

The app automatically switches based on `DATABASE_URL` environment variable.

---

## Static Files

### How it works:
1. Build time: `collectstatic` gathers all static files
2. Runtime: WhiteNoise serves static files
3. No separate static file server needed

### Configuration in settings.py:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added
    ...
]
```

---

## Deployment Checklist

### Before Deploying:

- [ ] Push Dockerfile to GitHub
- [ ] Push .dockerignore to GitHub
- [ ] Push render.yaml to GitHub (optional)
- [ ] Set SECRET_KEY in Render
- [ ] Set ALLOWED_HOSTS in Render
- [ ] Set DEBUG=False in Render
- [ ] Configure database (if using PostgreSQL)

### After Deployment:

- [ ] Test the app at your-app.onrender.com
- [ ] Check logs for any errors
- [ ] Test login functionality
- [ ] Test CV submission
- [ ] Test CV cards display
- [ ] Test admin panel access

---

## Troubleshooting

### Build Fails:
```bash
# Check Dockerfile syntax
docker build -t cvbook .

# Check logs
docker logs <container-id>
```

### App Returns 500:
- Check environment variables
- Check `DEBUG=False` is set
- Check `ALLOWED_HOSTS` includes your domain
- Check database connection

### Static Files Not Loading:
```bash
# Rebuild with static files
docker build --no-cache -t cvbook .

# Or run collectstatic manually in container
docker exec -it <container-id> python manage.py collectstatic
```

### Database Errors:
- Ensure DATABASE_URL is set correctly
- Run migrations:
  ```bash
  docker exec -it <container-id> python manage.py migrate
  ```

---

## Render-Specific Notes

### Free Tier Limitations:
- App sleeps after 15 min of inactivity
- 750 hours/month
- 512 MB RAM
- Shared CPU

### Custom Domain:
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records
4. Update ALLOWED_HOSTS

### Environment Variables:
- Set in Render dashboard
- Can be updated without redeployment
- Changes require app restart

---

## Alternative: Deploy Main Website (Port 8000)

The main UCA website can also be deployed with Docker. Let me know if you need a Dockerfile for that too!

---

## Summary

✅ **Dockerfile created** - Ready for Render deployment  
✅ **docker-compose.yml created** - For local testing  
✅ **.dockerignore created** - Optimized build  
✅ **render.yaml created** - Blueprint deployment  
✅ **Root URL fixed** - Shows login page instead of "OK"

**Your CV-Book is now Docker-ready for Render deployment!** 🚀

---

## Next Steps

1. **Test locally:**
   ```bash
   cd /home/user/UCA/CV-Book-for-Cooperative-Department
   docker-compose up
   ```

2. **Push to GitHub:**
   ```bash
   git add Dockerfile .dockerignore render.yaml docker-compose.yml
   git commit -m "Add Docker configuration for Render"
   git push
   ```

3. **Deploy on Render:**
   - Go to render.com
   - New → Web Service
   - Connect repository
   - Select Docker environment
   - Deploy!

---

*Deployment configuration ready!*

