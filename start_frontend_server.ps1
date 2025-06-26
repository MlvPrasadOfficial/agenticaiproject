# PowerShell script to start the frontend server
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   FRONTEND SERVER - ENTERPRISE INSIGHTS    " -ForegroundColor Cyan  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location "C:\AGENTICAIPROJECT\frontend"

Write-Host "📂 Current Directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies (if needed)..." -ForegroundColor Green
try {
    npm install --silent
    Write-Host "✅ Dependencies ready" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: npm install failed, trying to continue..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting Next.js development server..." -ForegroundColor Magenta
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Start the development server
npm run dev
