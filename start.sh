#!/bin/bash

# Render startup script for RABuddy backend
echo "🚀 Starting RABuddy backend on Render..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src/backend:/opt/render/project/src/backend/src"
export FLASK_ENV=production

# Create necessary directories
mkdir -p /opt/render/project/src/backend/chroma_store

# Start the application
echo "🌐 Starting Flask application..."
cd /opt/render/project/src
python backend/render_app.py
