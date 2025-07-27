@echo off
echo.
echo ========================================
echo     RABuddy System Status Check
echo ========================================
echo.

echo Checking local ports...
echo.
echo Port 3000 (Frontend):
netstat -ano | findstr ":3000" || echo   ✅ Available
echo.
echo Port 5000 (Backend):
netstat -ano | findstr ":5000" || echo   ✅ Available
echo.

echo ========================================
echo     Production Services
echo ========================================
echo.

echo Testing Backend Health...
curl -s https://rabuddy-backend.onrender.com/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend is running
) else (
    echo ❌ Backend is not responding
)
echo.

echo Testing API Endpoint...
curl -s https://rabuddy-backend.onrender.com/api/test 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API is working
) else (
    echo ❌ API is not responding
)
echo.

echo ========================================
echo     Quick Actions
echo ========================================
echo.
echo 1. Start local development: start_dev.bat
echo 2. Deploy to production: deploy.bat
echo 3. View deployment guide: DEPLOYMENT_GUIDE.md
echo.
echo Production URLs:
echo Frontend: https://rabuddy.abhiranmultani.com
echo Backend:  https://rabuddy-backend.onrender.com
echo.
pause
