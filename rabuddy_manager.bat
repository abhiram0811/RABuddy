@echo off
title RABuddy - Public Access Manager
color 0A

:MAIN_MENU
cls
echo.
echo  ██████╗  █████╗ ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗   ██╗
echo  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔══██╗██╔══██╗╚██╗ ██╔╝
echo  ██████╔╝███████║██████╔╝██║   ██║██║  ██║██║  ██║ ╚████╔╝ 
echo  ██╔══██╗██╔══██║██╔══██╗██║   ██║██║  ██║██║  ██║  ╚██╔╝  
echo  ██║  ██║██║  ██║██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║   
echo  ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   
echo.
echo  ====================================================
echo   Public Access Manager - Make RABuddy Global!
echo  ====================================================
echo.
echo  [1] Quick Setup - Start everything automatically
echo  [2] Manual Setup - Step by step guide
echo  [3] Update Public URLs - Change backend URL
echo  [4] Test Public Access - Verify everything works
echo  [5] View Current Status - Check what's running
echo  [6] Stop All Services - Clean shutdown
echo  [0] Exit
echo.
set /p choice="Select an option (0-6): "

if "%choice%"=="1" goto QUICK_SETUP
if "%choice%"=="2" goto MANUAL_SETUP  
if "%choice%"=="3" goto UPDATE_URLS
if "%choice%"=="4" goto TEST_ACCESS
if "%choice%"=="5" goto VIEW_STATUS
if "%choice%"=="6" goto STOP_SERVICES
if "%choice%"=="0" goto EXIT
goto MAIN_MENU

:QUICK_SETUP
cls
echo ========================================
echo   Quick Setup - Automated Public Access
echo ========================================
echo.
echo This will:
echo ✓ Start RABuddy backend (public version)
echo ✓ Start RABuddy frontend
echo ✓ Create ngrok tunnels
echo ✓ Guide you through final setup
echo.
pause
start_rabuddy_public.bat
echo.
echo After ngrok tunnels are created, press any key to update URLs...
pause
goto UPDATE_URLS

:MANUAL_SETUP
cls
echo ========================================
echo   Manual Setup Guide
echo ========================================
echo.
echo Step 1: Install ngrok (if not already done)
echo - Go to https://ngrok.com
echo - Create account and download ngrok
echo - Run: ngrok config add-authtoken YOUR_TOKEN
echo.
echo Step 2: Start RABuddy locally
echo - Backend: cd backend ^&^& python public_app.py
echo - Frontend: cd frontend ^&^& npm run dev
echo.
echo Step 3: Create tunnels
echo - Terminal 1: ngrok http 5001
echo - Terminal 2: ngrok http 3003
echo.
echo Step 4: Update frontend config
echo - Use option [3] to update URLs
echo.
echo Step 5: Test access
echo - Use option [4] to verify everything works
echo.
pause
goto MAIN_MENU

:UPDATE_URLS
cls
echo ========================================
echo   Update Public URLs
echo ========================================
echo.
update_public_urls.bat
echo.
echo URLs updated! Remember to restart your frontend.
echo.
pause
goto MAIN_MENU

:TEST_ACCESS
cls
echo ========================================
echo   Test Public Access
echo ========================================
echo.
test_public_access.bat
echo.
pause
goto MAIN_MENU

:VIEW_STATUS
cls
echo ========================================
echo   Current Status Check
echo ========================================
echo.
echo Checking local services...
echo.

REM Check if backend is running
netstat -an | find "5001" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend: Running on port 5001
) else (
    echo ❌ Backend: Not running
)

REM Check if frontend is running  
netstat -an | find "3003" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend: Running on port 3003
) else (
    echo ❌ Frontend: Not running
)

REM Check if ngrok is running
tasklist /FI "IMAGENAME eq ngrok.exe" 2>NUL | find /I /N "ngrok.exe" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ ngrok: Running (check terminals for URLs)
) else (
    echo ❌ ngrok: Not running
)

echo.
echo Current environment:
if exist "frontend\.env.local" (
    echo ✅ Frontend environment configured
    type "frontend\.env.local"
) else (
    echo ❌ Frontend environment not configured
)

echo.
pause
goto MAIN_MENU

:STOP_SERVICES
cls
echo ========================================
echo   Stopping All Services
echo ========================================
echo.
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

echo Stopping Node processes...
taskkill /F /IM node.exe 2>nul

echo Stopping ngrok processes...
taskkill /F /IM ngrok.exe 2>nul

echo.
echo ✅ All services stopped
echo.
pause
goto MAIN_MENU

:EXIT
cls
echo Thank you for using RABuddy Public Access Manager!
echo.
echo Your RABuddy is now globally accessible! 🌐
echo Share your ngrok frontend URL with anyone.
echo.
pause
exit
