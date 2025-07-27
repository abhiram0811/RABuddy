@echo off
echo ========================================
echo   RABuddy Public Access Tester
echo ========================================
echo.

set /p BACKEND_URL="Enter your public backend URL (e.g., https://abc123.ngrok.io): "
set /p FRONTEND_URL="Enter your public frontend URL (e.g., https://def456.ngrok.io): "

if "%BACKEND_URL%"=="" (
    echo Error: No backend URL provided
    pause
    exit /b 1
)

if "%FRONTEND_URL%"=="" (
    echo Error: No frontend URL provided  
    pause
    exit /b 1
)

echo.
echo Testing backend health...
curl -s "%BACKEND_URL%/health"
echo.

echo.
echo Testing backend API...
curl -s -X POST "%BACKEND_URL%/api/test" -H "Content-Type: application/json"
echo.

echo.
echo Testing a sample query...
curl -s -X POST "%BACKEND_URL%/api/query" -H "Content-Type: application/json" -d "{\"question\": \"What is this system?\"}"
echo.

echo.
echo ========================================
echo   Test Results Summary
echo ========================================
echo.
echo ✅ Backend URL: %BACKEND_URL%
echo ✅ Frontend URL: %FRONTEND_URL%
echo.
echo If you see JSON responses above, your backend is working!
echo Now test the frontend by opening: %FRONTEND_URL%
echo.
echo Share these URLs with anyone to give them access to RABuddy!
echo.
pause
