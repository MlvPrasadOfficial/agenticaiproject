"""
Enterprise Insights Copilot - Development Instructions
======================================================

CRITICAL POWERSHELL SYNTAX RULES:
- Use semicolon (;) instead of && for command chaining
- Use PowerShell-compatible paths and commands
- Always activate conda environment before running Python commands

BACKEND STARTUP SEQUENCE:
1. conda activate munna
2. cd backend
3. python main.py

FRONTEND STARTUP SEQUENCE:
1. cd frontend  
2. npm run dev

TESTING SEQUENCE:
1. conda activate munna
2. cd tests
3. python simple_demo.py

COMMON POWERSHELL PATTERNS:
- Multiple commands: command1; command2; command3
- Directory change + command: cd folder; python script.py
- Conda + Python: conda activate munna; python script.py

FILE STRUCTURE REMINDERS:
- Backend: c:\AGENTICAIPROJECT\backend\
- Frontend: c:\AGENTICAIPROJECT\frontend\
- Tests: c:\AGENTICAIPROJECT\tests\
- Sample Data: c:\AGENTICAIPROJECT\sample_sales_data.csv

DEBUGGING TIPS:
- Always check if conda environment is activated: (munna) should appear in prompt
- Backend runs on http://localhost:8000
- Frontend runs on http://localhost:3000
- Use 'Get-Process' to check running processes
- Use 'taskkill /f /pid <PID>' to force kill processes if needed

DEPENDENCY INSTALLATION:
- Backend: conda activate munna; cd backend; pip install -r requirements.txt
- Frontend: cd frontend; npm install

ERROR TROUBLESHOOTING:
1. Module not found: Check conda environment activation
2. Port already in use: Kill existing processes or use different port
3. Import errors: Ensure all dependencies are installed
4. Path issues: Use absolute paths when needed

DEPLOYMENT PREPARATION:
- Backend production: conda activate munna; cd backend; gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
- Frontend build: cd frontend; npm run build
- Environment variables: Set API keys in .env files
"""
