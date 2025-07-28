#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
Using production app with full RAG capabilities
"""
import os
import sys
from pathlib import Path

# Simple path setup
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the robust production app with full RAG
from robust_production_app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
