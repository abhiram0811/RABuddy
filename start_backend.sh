#!/bin/bash

echo "🚀 Starting RABuddy Backend with ChromaDB + Gemini"

# Load environment variables
if [ -f backend/.env ]; then
    echo "📄 Loading environment variables..."
    export $(grep -v '^#' backend/.env | xargs)
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

# Start the Flask backend
echo "🔧 Starting Flask backend on port 5001..."
cd backend
python app.py
