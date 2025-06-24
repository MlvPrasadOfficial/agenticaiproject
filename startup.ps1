# Enterprise Insights Copilot - PowerShell Startup Scripts
# Run these commands to start the full system

Write-Host "🚀 Enterprise Insights Copilot - PowerShell Startup" -ForegroundColor Green
Write-Host "=" * 60

# Function to start backend
function Start-Backend {
    Write-Host "🔧 Starting Backend Server..." -ForegroundColor Yellow
    conda activate munna; cd backend; python main.py
}

# Function to start frontend  
function Start-Frontend {
    Write-Host "⚛️ Starting Frontend Server..." -ForegroundColor Blue
    cd frontend; npm run dev
}

# Function to run tests
function Run-Tests {
    Write-Host "🧪 Running Tests..." -ForegroundColor Cyan
    conda activate munna; cd tests; python simple_demo.py
}

# Function to run specific test
function Run-TestSuite {
    Write-Host "🧪 Running Full Test Suite..." -ForegroundColor Cyan
    conda activate munna; cd tests; python test_runner.py
}

# Usage instructions
Write-Host "Available Commands:" -ForegroundColor White
Write-Host "  Start-Backend    - Start the FastAPI backend server" -ForegroundColor Gray
Write-Host "  Start-Frontend   - Start the Next.js frontend server" -ForegroundColor Gray  
Write-Host "  Run-Tests        - Run the three use cases demo" -ForegroundColor Gray
Write-Host "  Run-TestSuite    - Run comprehensive test suite" -ForegroundColor Gray

Write-Host "`nQuick Commands:" -ForegroundColor White
Write-Host "  Backend:   conda activate munna; cd backend; python main.py" -ForegroundColor Gray
Write-Host "  Frontend:  cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "  Tests:     conda activate munna; cd tests; python simple_demo.py" -ForegroundColor Gray
