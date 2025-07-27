@echo off
REM RABuddy Setup Script for Windows
REM This script helps set up the RABuddy application

echo 🤖 RABuddy Setup Script
echo =======================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Setup backend
echo.
echo 🐍 Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your API keys
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "chroma_store" mkdir chroma_store

echo ✅ Backend setup complete

REM Setup frontend
echo.
echo ⚛️  Setting up frontend...
cd ..\frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

REM Create .env.local file if it doesn't exist
if not exist ".env.local" (
    echo Creating .env.local file...
    copy .env.local.example .env.local
)

echo ✅ Frontend setup complete

REM Final instructions
echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Add your PDF documents to the 'pdfs/' directory
echo 2. Edit backend\.env with your OpenRouter API key
echo 3. Start the backend: cd backend ^&^& python app.py
echo 4. Start the frontend: cd frontend ^&^& npm run dev
echo.
echo Access the application at http://localhost:3000

pause
