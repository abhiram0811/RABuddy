@echo off
echo Starting RABuddy backend...
start "RABuddy Backend" cmd /k "cd /d c:\Users\mabhi\OneDrive\Desktop\RABuddy\backend && python minimal_app.py"

echo Starting RABuddy frontend...
start "RABuddy Frontend" cmd /k "cd /d c:\Users\mabhi\OneDrive\Desktop\RABuddy && npm run dev"

echo RABuddy is starting up...
echo Backend will be at: http://localhost:5001
echo Frontend will be at: http://localhost:3002
pause
