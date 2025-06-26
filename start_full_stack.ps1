# Combined startup script for both backend and frontend
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  ENTERPRISE INSIGHTS COPILOT - FULL STACK  " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\AGENTICAIPROJECT"
Set-Location $projectRoot

Write-Host "🔍 Checking if backend is already running..." -ForegroundColor Yellow

# Check if backend is running
try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Method GET -TimeoutSec 3 -UseBasicParsing
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host "✅ Backend is already running on port 8000" -ForegroundColor Green
        $backendRunning = $true
    }
} catch {
    Write-Host "❌ Backend not running, will start it" -ForegroundColor Red
    $backendRunning = $false
}

# Check if frontend is running
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 3 -UseBasicParsing
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "✅ Frontend is already running on port 3000" -ForegroundColor Green
        $frontendRunning = $true
    }
} catch {
    Write-Host "❌ Frontend not running, will start it" -ForegroundColor Red
    $frontendRunning = $false
}

Write-Host ""

if (-not $backendRunning) {
    Write-Host "🚀 Starting Backend Server..." -ForegroundColor Magenta
    Write-Host "Opening new terminal for backend..." -ForegroundColor Gray
    
    # Start backend in new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; python main.py"
    
    Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Verify backend started
    try {
        $backendVerify = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Method GET -TimeoutSec 10 -UseBasicParsing
        if ($backendVerify.StatusCode -eq 200) {
            Write-Host "✅ Backend started successfully!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Backend might still be starting..." -ForegroundColor Yellow
    }
}

if (-not $frontendRunning) {
    Write-Host "🚀 Starting Frontend Server..." -ForegroundColor Magenta
    Write-Host "Opening new terminal for frontend..." -ForegroundColor Gray
    
    # Start frontend in new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; npm run dev"
    
    Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎉 STARTUP COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Backend Health: http://localhost:8000/api/v1/health" -ForegroundColor Gray
Write-Host "===============================================" -ForegroundColor Cyan

# Open frontend in browser
Write-Host ""
Write-Host "🌐 Opening frontend in browser..." -ForegroundColor Magenta
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ All services should be running!" -ForegroundColor Green
Write-Host "Check the new terminal windows for server logs." -ForegroundColor Gray
