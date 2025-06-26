@echo off
echo 🚀 Starting Frontend Development Server...
echo.

cd /d "c:\AGENTICAIPROJECT\frontend"

echo 📦 Installing dependencies (if needed)...
call npm install

echo.
echo 🎯 Starting Next.js development server...
echo The frontend will be available at: http://localhost:3000
echo.
echo ⚠️  Keep this window open while using the application
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
