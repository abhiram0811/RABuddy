@echo off
echo Starting RABuddy Development Environment...

echo.
echo Killing any existing processes on ports 3000 and 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo.
echo Starting backend on port 5000...
cd backend
start "RABuddy Backend" cmd /k "python src/app.py"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting frontend on port 3000...
cd ../frontend
start "RABuddy Frontend" cmd /k "npm run dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
pause >nul
