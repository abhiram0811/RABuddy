@echo off
echo ========================================
echo   RABuddy Public Access Setup
echo ========================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ngrok is not installed or not in PATH
    echo.
    echo To install ngrok:
    echo 1. Go to https://ngrok.com and create a free account
    echo 2. Download ngrok for Windows
    echo 3. Extract to a folder and add to PATH
    echo 4. Run: ngrok config add-authtoken YOUR_TOKEN
    echo.
    pause
    exit /b 1
)

echo Starting RABuddy backend (public version)...
start "RABuddy Backend Public" cmd /k "cd /d c:\Users\mabhi\OneDrive\Desktop\RABuddy\backend && python public_app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting RABuddy frontend...
start "RABuddy Frontend" cmd /k "cd /d c:\Users\mabhi\OneDrive\Desktop\RABuddy\frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Creating Public Tunnels
echo ========================================

REM Create backend tunnel with custom subdomain if available
echo Creating backend tunnel...
start "Backend Tunnel" cmd /k "ngrok http 5001 --log stdout"

timeout /t 3 /nobreak >nul

REM Create frontend tunnel with custom subdomain if available  
echo Creating frontend tunnel...
start "Frontend Tunnel" cmd /k "ngrok http 3003 --log stdout"

echo.
echo ========================================
echo   SETUP INSTRUCTIONS
echo ========================================
echo.
echo 1. Look at the ngrok terminal windows for your public URLs
echo 2. Backend tunnel (port 5001): Copy the HTTPS URL
echo 3. Frontend tunnel (port 3003): This is your public RABuddy URL
echo.
echo 4. Update the frontend environment:
echo    - Run: update_public_urls.bat
echo    - Enter your backend ngrok URL when prompted
echo.
echo 5. After updating, restart frontend:
echo    - Close the frontend terminal
echo    - Run: cd frontend ^&^& npm run dev
echo.
echo 🌐 Your RABuddy will be publicly accessible!
echo 📱 Share the frontend URL with anyone
echo.
pause
