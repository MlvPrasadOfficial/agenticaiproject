# PowerShell Quick Reference for Enterprise Insights Copilot

## 🚀 **QUICK START COMMANDS**

### Start Backend Server
```powershell
conda activate munna; cd backend; python main.py
```

### Start Frontend Server  
```powershell
cd frontend; npm run dev
```

### Run Three Use Cases Demo
```powershell
conda activate munna; cd tests; python simple_demo.py
```

### Run Full Test Suite
```powershell
conda activate munna; cd tests; python test_runner.py
```

## 🔧 **DEVELOPMENT COMMANDS**

### Install Backend Dependencies
```powershell
conda activate munna; cd backend; pip install -r requirements.txt
```

### Install Frontend Dependencies
```powershell
cd frontend; npm install
```

### Run Integration Tests
```powershell
conda activate munna; cd tests; python integration_test.py
```

### Check Server Health
```powershell
# Backend health check
curl http://localhost:8000/health

# Or using PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

## 🛠️ **TROUBLESHOOTING**

### Check Running Processes
```powershell
# Check what's running on port 8000 (backend)
Get-NetTCPConnection -LocalPort 8000

# Check what's running on port 3000 (frontend)  
Get-NetTCPConnection -LocalPort 3000
```

### Kill Processes if Stuck
```powershell
# Kill process by port
$process = Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $process -Force

# Or kill by name
Stop-Process -Name "python" -Force
Stop-Process -Name "node" -Force
```

### Check Conda Environment
```powershell
# List environments
conda env list

# Activate environment
conda activate munna

# Check Python path
Get-Command python
```

## 📝 **FILE OPERATIONS**

### Navigate to Project Directories
```powershell
# Main project
cd C:\AGENTICAIPROJECT

# Backend
cd C:\AGENTICAIPROJECT\backend

# Frontend  
cd C:\AGENTICAIPROJECT\frontend

# Tests
cd C:\AGENTICAIPROJECT\tests
```

### View Logs (if needed)
```powershell
# View last 50 lines of a log file
Get-Content -Path "logfile.txt" -Tail 50

# Follow log file (like tail -f)
Get-Content -Path "logfile.txt" -Wait
```

## 🎯 **TESTING WORKFLOWS**

### Test SQL Queries
```powershell
conda activate munna; cd tests; python test_sql_queries.py
```

### Test Insight Generation
```powershell
conda activate munna; cd tests; python test_insight_queries.py
```

### Test Chart Generation
```powershell
conda activate munna; cd tests; python test_chart_queries.py
```

## 🚢 **PRODUCTION COMMANDS**

### Build for Production
```powershell
# Build frontend
cd frontend; npm run build

# Start production backend
conda activate munna; cd backend; gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

---

**💡 Remember**: PowerShell uses `;` for command chaining, not `&&` like Bash!
