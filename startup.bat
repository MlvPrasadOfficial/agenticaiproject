@echo off
REM Enterprise Insights Copilot - Windows Batch Startup
echo 🚀 Enterprise Insights Copilot - Windows Startup
echo ============================================================

REM Set variables
set CONDA_ENV=munna
set BACKEND_DIR=backend
set FRONTEND_DIR=frontend
set TESTS_DIR=tests

echo Available startup options:
echo.
echo 1. Start Backend Server
echo 2. Start Frontend Server  
echo 3. Run Tests Demo
echo 4. Start Both (Backend + Frontend)
echo 5. Show Manual Commands
echo.

choice /c 12345 /m "Select option"

if %errorlevel%==1 goto backend
if %errorlevel%==2 goto frontend
if %errorlevel%==3 goto tests
if %errorlevel%==4 goto both
if %errorlevel%==5 goto manual

:backend
echo 🔧 Starting Backend Server...
call conda activate %CONDA_ENV% && cd %BACKEND_DIR% && python main.py
goto end

:frontend
echo ⚛️ Starting Frontend Server...
cd %FRONTEND_DIR% && npm run dev
goto end

:tests
echo 🧪 Running Tests Demo...
call conda activate %CONDA_ENV% && cd %TESTS_DIR% && python simple_demo.py
goto end

:both
echo 🚀 Starting Both Servers...
echo 🔧 Backend will start first, then open another terminal for frontend
call conda activate %CONDA_ENV% && cd %BACKEND_DIR% && start "Backend Server" python main.py
timeout /t 3
cd .. && cd %FRONTEND_DIR% && start "Frontend Server" npm run dev
goto end

:manual
echo.
echo 📋 Manual Commands (copy and paste):
echo.
echo Backend:  conda activate munna ^& cd backend ^& python main.py
echo Frontend: cd frontend ^& npm run dev  
echo Tests:    conda activate munna ^& cd tests ^& python simple_demo.py
echo.
echo 💡 Use ^& in cmd or ; in PowerShell for command chaining
goto end

:end
echo.
echo ✅ Startup script completed!
pause
