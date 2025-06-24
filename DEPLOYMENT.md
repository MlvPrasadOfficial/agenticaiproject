# CI/CD Setup Instructions

## GitHub Actions Workflow

This repository contains a GitHub Actions workflow for CI/CD automation in `.github/workflows/main.yml`. To enable the automated deployments, you'll need to set up the following secrets in your GitHub repository:

### For Render Deployment
1. `RENDER_API_KEY` - Your Render API key for authentication
2. `RENDER_DEPLOY_HOOK_URL` - The deploy hook URL from your Render service

### For Vercel Deployment
1. `VERCEL_TOKEN` - Your Vercel authentication token
2. `VERCEL_ORG_ID` - Your Vercel organization ID
3. `VERCEL_PROJECT_ID` - Your Vercel project ID

## Setting Up Secrets in GitHub

1. Go to your repository on GitHub
2. Click on "Settings" > "Secrets" > "Actions"
3. Click "New repository secret"
4. Add each of the required secrets mentioned above

## Manual Deployment

If you prefer to deploy manually:

### Backend (Render)
1. Follow the instructions at https://render.com/docs to set up a new Web Service
2. Connect your GitHub repository
3. Set the build command to `cd backend && pip install -r requirements.txt`
4. Set the start command to `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Follow the instructions at https://vercel.com/docs to set up a new project
2. Connect your GitHub repository
3. Set the root directory to `frontend`
4. Vercel will automatically detect the Next.js configuration
