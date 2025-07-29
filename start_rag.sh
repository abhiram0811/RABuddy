#!/bin/bash
echo "🚀🔥 FORCE RAG DEPLOYMENT SCRIPT 🔥🚀"

# Install ALL dependencies from requirements.txt
echo "📦 Installing all dependencies..."
pip install --no-cache-dir -r requirements.txt

# Navigate to backend and start guaranteed RAG app
echo "🎯 Starting guaranteed RAG app..."
cd backend
python guaranteed_rag_app.py
