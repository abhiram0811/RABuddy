@echo off
echo ========================================
echo   RABuddy Environment Updater
echo ========================================
echo.

set /p BACKEND_URL="Enter your ngrok backend URL (e.g., https://abc123.ngrok.io): "

if "%BACKEND_URL%"=="" (
    echo Error: No URL provided
    pause
    exit /b 1
)

REM Remove trailing slash if present
if "%BACKEND_URL:~-1%"=="/" set BACKEND_URL=%BACKEND_URL:~0,-1%

echo.
echo Updating frontend environment...

REM Create new .env.local with the backend URL
echo NEXT_PUBLIC_API_URL=%BACKEND_URL%/api > frontend\.env.local

echo.
echo ✅ Environment updated successfully!
echo Backend API URL set to: %BACKEND_URL%/api
echo.
echo Now restart your frontend:
echo cd frontend
echo npm run dev
echo.
pause
