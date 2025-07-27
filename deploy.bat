@echo off
echo.
echo ========================================
echo   RABuddy Production Deployment
echo ========================================
echo.

echo 1. Checking Git status...
git status --porcelain
if %ERRORLEVEL% NEQ 0 (
    echo Error: Not a git repository or git not found
    pause
    exit /b 1
)

echo.
echo 2. Adding all changes to git...
git add .

echo.
echo 3. Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg="Update deployment configuration"
git commit -m "%commit_msg%"

echo.
echo 4. Pushing to repository...
git push

echo.
echo ========================================
echo   Deployment Status
echo ========================================
echo.
echo ✅ Backend: Already running on Render
echo    URL: https://rabuddy-backend.onrender.com
echo.
echo 🔄 Frontend: Deploying to Vercel (triggered by git push)
echo    URL: https://rabuddy.abhiranmultani.com
echo.
echo 📝 Monitor deployment:
echo    - Vercel: https://vercel.com/dashboard
echo    - Render: https://dashboard.render.com
echo.

echo Testing backend health...
curl -s https://rabuddy-backend.onrender.com/health
echo.
echo.

echo Deployment process initiated!
echo Frontend should be live in 2-3 minutes.
echo.
pause
