# Production Deployment Guide

## Overview
This guide covers deploying the Enterprise Insights Copilot to production using:
- **Frontend**: Vercel (Next.js 14)
- **Backend**: Render (FastAPI)
- **Database**: PostgreSQL + Redis
- **Vector Store**: Pinecone
- **Domain**: Custom domain with SSL

## Pre-deployment Checklist

### 1. Code Preparation
- [ ] All tests passing (`npm test` and `pytest`)
- [ ] Code linted and formatted
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] Build scripts tested locally

### 2. External Services
- [ ] Pinecone account and index created
- [ ] PostgreSQL database provisioned
- [ ] Redis instance available
- [ ] Domain name registered
- [ ] SSL certificates ready

### 3. Security Review
- [ ] API keys secured
- [ ] CORS origins configured
- [ ] Rate limiting implemented
- [ ] Input validation complete
- [ ] Security headers configured

## Backend Deployment (Render)

### Step 1: Prepare Repository
```bash
# Ensure backend has all required files
cd backend/
ls -la
# Should see: main.py, requirements.txt, render.yaml, build.sh
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new **Web Service**
4. Select your repository and `backend` folder
5. Configure build and start commands:
   ```bash
   # Build Command
   chmod +x build.sh && ./build.sh
   
   # Start Command  
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### Step 3: Configure Environment Variables
```bash
# Core Application
ENVIRONMENT=production
DEBUG=false
PROJECT_NAME=Enterprise Insights Copilot
API_V1_STR=/api/v1

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port

# AI Services
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
OLLAMA_HOST=http://localhost:11434

# Security
SECRET_KEY=your_64_char_secret_key
ALLOWED_ORIGINS=https://yourdomain.com,https://yourapp.vercel.app

# File Upload
MAX_FILE_SIZE=104857600
UPLOAD_PATH=/tmp/uploads
```

### Step 4: Deploy and Verify
1. Click **Create Web Service**
2. Wait for deployment to complete
3. Test health endpoint: `https://yourapp.onrender.com/health`
4. Verify API docs: `https://yourapp.onrender.com/docs`

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository
```bash
# Ensure frontend has required files
cd frontend/
ls -la
# Should see: package.json, next.config.ts, vercel.json
```

### Step 2: Deploy to Vercel
```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from frontend directory
cd frontend/
vercel --prod
```

### Step 3: Configure Environment Variables
In Vercel dashboard:
```bash
NEXT_PUBLIC_API_URL=https://yourbackend.onrender.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_APP_NAME=Enterprise Insights Copilot
```

### Step 4: Custom Domain Setup
1. Go to Vercel project settings
2. Add custom domain
3. Configure DNS records:
   ```
   Type: CNAME
   Name: www (or @)
   Value: cname.vercel-dns.com
   ```
4. Wait for SSL provisioning

## Database Setup

### PostgreSQL Migration
```bash
# Connect to production database
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Run migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### Redis Configuration
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
# Should return: PONG
```

## Pinecone Vector Database Setup

### Create Index
```python
import pinecone

# Initialize Pinecone
pinecone.init(
    api_key="your_api_key",
    environment="us-east-1"
)

# Create index
pinecone.create_index(
    name="enterprise-insights",
    dimension=384,  # for all-MiniLM-L6-v2
    metric="cosine",
    spec=pinecone.ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
```

### Verify Index
```bash
# Test Pinecone connection
curl -X GET "https://yourbackend.onrender.com/api/v1/rag/health"
```

## Domain and SSL Configuration

### DNS Setup
```bash
# For Vercel (Frontend)
Type: CNAME
Name: www
Value: cname.vercel-dns.com

# For Render (Backend API)
Type: CNAME  
Name: api
Value: your-app.onrender.com
```

### SSL Verification
```bash
# Check SSL certificate
curl -I https://yourdomain.com
curl -I https://api.yourdomain.com

# Verify security headers
curl -I https://yourdomain.com | grep -i security
```

## Post-Deployment Verification

### Health Checks
```bash
# Frontend health
curl https://yourdomain.com/api/health

# Backend health
curl https://api.yourdomain.com/health

# RAG system health
curl https://api.yourdomain.com/api/v1/rag/health
```

### Feature Testing
```bash
# Test file upload
curl -X POST https://api.yourdomain.com/api/v1/upload/files/upload \
  -F "file=@test.csv"

# Test AI agents
curl -X POST https://api.yourdomain.com/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'

# Test RAG search
curl -X POST https://api.yourdomain.com/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test search", "top_k": 5}'
```

### Performance Monitoring
```bash
# Load testing with Apache Bench
ab -n 100 -c 10 https://api.yourdomain.com/health

# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com
```

## Monitoring and Alerts

### Render Monitoring
- Enable health checks: `/health`
- Set up log monitoring
- Configure auto-scaling if needed

### Vercel Analytics
- Enable Vercel Analytics
- Monitor Core Web Vitals
- Set up error tracking

### Custom Monitoring
```python
# Add to your monitoring service
import requests
import time

def monitor_endpoints():
    endpoints = [
        "https://yourdomain.com/api/health",
        "https://api.yourdomain.com/health",
        "https://api.yourdomain.com/api/v1/rag/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code != 200:
                send_alert(f"Endpoint down: {endpoint}")
        except Exception as e:
            send_alert(f"Error checking {endpoint}: {e}")

# Run every 5 minutes
```

## Backup and Disaster Recovery

### Database Backups
```bash
# Automated daily backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Upload to cloud storage
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

### Pinecone Backup
```python
# Export vector data
import pinecone

# Connect to index
index = pinecone.Index("enterprise-insights")

# Fetch all vectors (in batches)
all_vectors = []
for ids in batch_ids:
    vectors = index.fetch(ids=ids)
    all_vectors.extend(vectors)

# Save to backup file
with open("pinecone_backup.json", "w") as f:
    json.dump(all_vectors, f)
```

### Code Backups
- Repository automatically backed up on GitHub
- Deployment artifacts stored by Vercel/Render
- Environment variables documented separately

## Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs in Render dashboard
# Common fixes:
- Update Python version in render.yaml
- Fix requirements.txt dependencies
- Check build.sh permissions
```

#### 2. CORS Errors
```bash
# Update ALLOWED_ORIGINS in backend
ALLOWED_ORIGINS=https://yourdomain.com,https://yourapp.vercel.app
```

#### 3. Database Connection Issues
```bash
# Verify DATABASE_URL format
postgresql://username:password@hostname:port/database_name

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### 4. Pinecone Errors
```bash
# Check API key and environment
curl -X GET "https://controller.pinecone.io/actions/whoami" \
  -H "Api-Key: YOUR_API_KEY"
```

### Recovery Procedures

#### Application Rollback
```bash
# Revert to previous deployment
vercel --prod --force  # Frontend
# Use Render dashboard for backend rollback
```

#### Database Recovery
```bash
# Restore from backup
psql $DATABASE_URL < backup_20240628.sql
```

#### Emergency Contacts
- DevOps Team: devops@company.com
- Database Admin: dba@company.com
- Security Team: security@company.com

## Success Criteria

### Performance Targets
- Page load time: < 2 seconds
- API response time: < 500ms
- Uptime: > 99.9%

### Security Requirements
- SSL/TLS enabled
- Security headers configured
- API keys secured
- CORS properly configured

### Monitoring Requirements
- Health checks active
- Error tracking enabled
- Performance monitoring set up
- Backup strategy implemented

## Next Steps

After successful deployment:
1. Set up continuous monitoring
2. Configure automatic scaling
3. Implement backup automation
4. Set up staging environment
5. Plan for blue-green deployments
6. Document runbooks for operations team

---

**🎉 Congratulations! Your Enterprise Insights Copilot is now live in production!**
