#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
Using minimal debug app for now to ensure deployment works
"""
import os
import sys
from pathlib import Path

# Simple path setup
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the minimal debug app that we know works
from minimal_debug_app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
