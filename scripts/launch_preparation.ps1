# Production Launch Preparation Script (PowerShell)
# Enterprise Insights Copilot

param(
    [switch]$SkipTests,
    [switch]$QuickCheck
)

# Color functions for PowerShell
function Write-Status { 
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue 
}

function Write-Success { 
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green 
}

function Write-Warning { 
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow 
}

function Write-Error { 
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red 
}

function Test-CommandExists {
    param($Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Main header
Write-Host "🚀 Enterprise Insights Copilot - Production Launch Preparation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check Node.js
    if (Test-CommandExists "node") {
        $nodeVersion = node --version
        Write-Success "Node.js found: $nodeVersion"
    } else {
        Write-Error "Node.js not found. Please install Node.js 18+ and try again."
        exit 1
    }
    
    # Check Python
    if (Test-CommandExists "python") {
        $pythonVersion = python --version
        Write-Success "Python found: $pythonVersion"
    } else {
        Write-Error "Python not found. Please install Python 3.11+ and try again."
        exit 1
    }
    
    # Check Git
    if (Test-CommandExists "git") {
        Write-Success "Git found"
    } else {
        Write-Error "Git not found. Please install Git and try again."
        exit 1
    }
    
    # Check Vercel CLI
    if (Test-CommandExists "vercel") {
        Write-Success "Vercel CLI found"
    } else {
        Write-Warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    }
}

# Pre-flight checks
function Test-PreflightChecks {
    Write-Status "Running pre-flight checks..."
    
    # Check if in correct directory
    if (-not (Test-Path "task_execution_table.md")) {
        Write-Error "Please run this script from the project root directory"
        exit 1
    }
    
    # Check frontend directory
    if (-not (Test-Path "frontend")) {
        Write-Error "Frontend directory not found"
        exit 1
    }
    
    # Check backend directory
    if (-not (Test-Path "backend")) {
        Write-Error "Backend directory not found"
        exit 1
    }
    
    Write-Success "Directory structure verified"
}

# Frontend preparation
function Prepare-Frontend {
    Write-Status "Preparing frontend for deployment..."
    
    Push-Location frontend
    
    try {
        # Install dependencies
        Write-Status "Installing frontend dependencies..."
        npm ci
        
        if (-not $SkipTests) {
            # Run linting
            Write-Status "Running ESLint..."
            npm run lint
            
            # Run type checking
            Write-Status "Running TypeScript type check..."
            if (Get-Command "npm run type-check" -ErrorAction SilentlyContinue) {
                npm run type-check
            }
            
            # Run tests
            Write-Status "Running frontend tests..."
            npm test -- --passWithNoTests --watchAll=false
        }
        
        # Build frontend
        Write-Status "Building frontend..."
        npm run build
        
        Write-Success "Frontend preparation complete"
    }
    catch {
        Write-Error "Frontend preparation failed: $_"
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Backend preparation
function Prepare-Backend {
    Write-Status "Preparing backend for deployment..."
    
    Push-Location backend
    
    try {
        # Check for requirements.txt
        if (-not (Test-Path "requirements.txt")) {
            Write-Error "requirements.txt not found in backend directory"
            exit 1
        }
        
        # Install dependencies (assuming virtual environment is set up)
        Write-Status "Installing backend dependencies..."
        pip install -r requirements.txt
        
        if (-not $SkipTests) {
            # Run tests
            Write-Status "Running backend tests..."
            if (Test-Path "tests") {
                pytest tests/ -v
            } else {
                Write-Warning "No tests directory found"
            }
        }
        
        Write-Success "Backend preparation complete"
    }
    catch {
        Write-Error "Backend preparation failed: $_"
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Environment validation
function Test-Environment {
    Write-Status "Validating environment configuration..."
    
    # Check for environment files
    if (-not (Test-Path "backend\.env.example")) {
        Write-Warning "Backend .env.example not found"
    }
    
    if (-not (Test-Path "frontend\.env.example")) {
        Write-Warning "Frontend .env.example not found"
    }
    
    # Validate backend config
    Push-Location backend
    try {
        Write-Status "Validating backend configuration..."
        python -c @"
from app.core.config import settings
print(f'✓ Project: {settings.PROJECT_NAME}')
print(f'✓ Version: {settings.VERSION}')
print(f'✓ Environment: {settings.ENVIRONMENT}')
"@
        Write-Success "Backend configuration valid"
    }
    catch {
        Write-Error "Backend configuration invalid: $_"
    }
    finally {
        Pop-Location
    }
}

# Security checks
function Test-Security {
    Write-Status "Running security checks..."
    
    # Check for sensitive files
    if (Test-Path "backend\.env") {
        Write-Warning "Found backend\.env file - ensure it's not committed to git"
    }
    
    if (Test-Path "frontend\.env.local") {
        Write-Warning "Found frontend\.env.local file - ensure it's not committed to git"
    }
    
    # Check gitignore
    if (Test-Path ".gitignore") {
        $gitignoreContent = Get-Content ".gitignore" -Raw
        if ($gitignoreContent -match "\.env") {
            Write-Success "Environment files properly ignored in git"
        } else {
            Write-Warning "Environment files may not be properly ignored"
        }
    }
    
    Write-Success "Security checks complete"
}

# Documentation check
function Test-Documentation {
    Write-Status "Checking documentation..."
    
    $requiredDocs = @(
        "README.md",
        "docs\DEPLOYMENT_GUIDE.md",
        "docs\ENVIRONMENT_SETUP.md"
    )
    
    foreach ($doc in $requiredDocs) {
        if (Test-Path $doc) {
            Write-Success "Found: $doc"
        } else {
            Write-Warning "Missing: $doc"
        }
    }
    
    Write-Success "Documentation check complete"
}

# Deployment checklist
function Show-DeploymentChecklist {
    Write-Status "Final deployment checklist..."
    
    Write-Host ""
    Write-Host "📋 PRE-DEPLOYMENT CHECKLIST" -ForegroundColor Cyan
    Write-Host "===========================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Backend (Render):"
    Write-Host "  □ Environment variables configured"
    Write-Host "  □ Database connection tested"
    Write-Host "  □ Pinecone API key verified"
    Write-Host "  □ Health endpoint accessible"
    Write-Host "  □ Build script executable"
    Write-Host ""
    Write-Host "Frontend (Vercel):"
    Write-Host "  □ API URL configured"
    Write-Host "  □ Build successful"
    Write-Host "  □ Environment variables set"
    Write-Host "  □ Custom domain ready"
    Write-Host "  □ SSL certificate active"
    Write-Host ""
    Write-Host "External Services:"
    Write-Host "  □ Pinecone index created"
    Write-Host "  □ PostgreSQL database ready"
    Write-Host "  □ Redis instance available"
    Write-Host "  □ Domain DNS configured"
    Write-Host "  □ Monitoring tools set up"
    Write-Host ""
    
    $confirm = Read-Host "All items checked? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Success "Pre-deployment checklist completed!"
    } else {
        Write-Warning "Please complete the checklist before deploying"
        exit 1
    }
}

# Generate deployment commands
function New-DeploymentCommands {
    Write-Status "Generating deployment commands..."
    
    $deploymentScript = @"
# Deployment Commands for Enterprise Insights Copilot
# Run these commands to deploy to production

Write-Host "🚀 Deploying Enterprise Insights Copilot to Production" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Deploy Frontend to Vercel
Write-Host "📱 Deploying Frontend..." -ForegroundColor Blue
Set-Location frontend
vercel --prod
Set-Location ..

# Deploy Backend to Render
Write-Host "🖥️  Backend deployment will be triggered automatically on git push" -ForegroundColor Blue
Write-Host "   Push your changes to trigger Render deployment:"
Write-Host "   git add ."
Write-Host "   git commit -m 'Production deployment'"
Write-Host "   git push origin main"

Write-Host ""
Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Useful Links:"
Write-Host "   Frontend: https://yourapp.vercel.app"
Write-Host "   Backend: https://yourapp.onrender.com"
Write-Host "   API Docs: https://yourapp.onrender.com/docs"
Write-Host "   Health Check: https://yourapp.onrender.com/health"
Write-Host ""
Write-Host "📊 Monitor deployment status:"
Write-Host "   Vercel: https://vercel.com/dashboard"
Write-Host "   Render: https://dashboard.render.com"
"@

    $deploymentScript | Out-File -FilePath "deployment_commands.ps1" -Encoding UTF8
    Write-Success "Deployment commands generated: .\deployment_commands.ps1"
}

# Main execution
function Main {
    Write-Host ""
    Write-Status "Starting production launch preparation..."
    Write-Host ""
    
    Test-Prerequisites
    Test-PreflightChecks
    
    if (-not $QuickCheck) {
        Prepare-Frontend
        Prepare-Backend
        Test-Environment
        Test-Security
        Test-Documentation
        Show-DeploymentChecklist
        New-DeploymentCommands
    } else {
        Write-Status "Quick check mode - skipping detailed preparation"
        Test-Environment
        Test-Documentation
    }
    
    Write-Host ""
    Write-Success "🎉 Production launch preparation completed successfully!"
    Write-Host ""
    Write-Status "Next steps:"
    Write-Host "  1. Review the deployment checklist above"
    Write-Host "  2. Configure environment variables in Vercel and Render"
    Write-Host "  3. Run .\deployment_commands.ps1 to deploy"
    Write-Host "  4. Monitor deployment status and test endpoints"
    Write-Host "  5. Set up monitoring and alerts"
    Write-Host ""
    Write-Status "Documentation available in docs\ directory"
    Write-Host ""
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Script failed: $_"
    exit 1
}
