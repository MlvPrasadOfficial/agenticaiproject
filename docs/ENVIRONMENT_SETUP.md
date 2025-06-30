# Environment Variables Configuration

## Required Environment Variables

### Backend (Render)
Create these environment variables in your Render dashboard:

```bash
# Core Application
ENVIRONMENT=production
DEBUG=false
PROJECT_NAME="Enterprise Insights Copilot"
VERSION=1.0.0
API_V1_STR=/api/v1

# Database & Storage
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://localhost:6379

# AI & LLM Configuration
OLLAMA_HOST=http://localhost:11434
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=enterprise-insights

# Security
SECRET_KEY=your_super_secret_key_here_64_chars_minimum
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=https://enterprise-insights-frontend.vercel.app,http://localhost:3000

# File Upload
MAX_FILE_SIZE=104857600
UPLOAD_PATH=/tmp/uploads
ALLOWED_FILE_TYPES=csv,xlsx,xls,json,txt,pdf

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

### Frontend (Vercel)
Set these in your Vercel project settings:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://enterprise-insights-backend.render.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_APP_NAME=Enterprise Insights Copilot

# Analytics (Optional)
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id_here

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_DEBUG=false
```

## Local Development
Copy `.env.example` to `.env` and fill in your values:

```bash
# Backend .env
cp backend/.env.example backend/.env

# Frontend .env.local  
cp frontend/.env.example frontend/.env.local
```

## Security Notes

1. **Never commit real environment variables to version control**
2. **Use strong, unique values for SECRET_KEY**
3. **Restrict CORS origins to your actual domains**
4. **Use environment-specific API keys**
5. **Enable SSL/TLS in production**

## Database Setup

### PostgreSQL (Recommended for Production)
```bash
# Create database
createdb enterprise_insights

# Run migrations
alembic upgrade head
```

### Redis (For Caching)
```bash
# Start Redis server
redis-server

# Test connection
redis-cli ping
```

## External Services Setup

### Pinecone Vector Database
1. Create account at [pinecone.io](https://pinecone.io)
2. Create new index with:
   - Dimension: 384 (for all-MiniLM-L6-v2)
   - Metric: cosine
   - Cloud: AWS
   - Region: us-east-1

### Ollama Setup (Optional for Local LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama model
ollama pull llama3.1:8b

# Start Ollama server
ollama serve
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Pinecone index created
- [ ] Domain DNS configured
- [ ] SSL certificates active
- [ ] Health checks passing
- [ ] Logs monitoring setup
- [ ] Backup strategy in place
