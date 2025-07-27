#!/bin/bash

# RABuddy Setup Script
# This script helps set up the RABuddy application

echo "🤖 RABuddy Setup Script"
echo "======================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo ""
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys"
fi

# Create necessary directories
mkdir -p logs chroma_store

echo "✅ Backend setup complete"

# Setup frontend
echo ""
echo "⚛️  Setting up frontend..."
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.local.example .env.local
fi

echo "✅ Frontend setup complete"

# Final instructions
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your PDF documents to the 'pdfs/' directory"
echo "2. Edit backend/.env with your OpenRouter API key"
echo "3. Start the backend: cd backend && python app.py"
echo "4. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Access the application at http://localhost:3000"
