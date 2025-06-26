@echo off
title Frontend Server - Enterprise Insights Copilot
color 0B
echo.
echo ===============================================
echo    FRONTEND SERVER - ENTERPRISE INSIGHTS     
echo ===============================================
echo.
echo Backend Status: Checking connection...

REM Check if backend is running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/health' -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { Write-Host 'Backend: CONNECTED (Port 8000)' -ForegroundColor Green } } catch { Write-Host 'Backend: NOT RUNNING' -ForegroundColor Red }"

echo.
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

cd /d "C:\AGENTICAIPROJECT\frontend"

echo Installing dependencies (if needed)...
call npm install --silent

echo.
echo Starting development server...
call npm run dev

echo.
echo Frontend server stopped.
pause
