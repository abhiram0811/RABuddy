#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
Using robust production app with full RAG capabilities - v2.0
"""
import os
import sys
from pathlib import Path

# Simple path setup
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the robust production app with full RAG
try:
    from robust_production_app import app
    print("✅ Successfully imported robust_production_app")
except ImportError as e:
    print(f"❌ Failed to import robust_production_app: {e}")
    # Fallback to production_app if robust one fails
    try:
        from production_app import app
        print("✅ Fallback: Successfully imported production_app")
    except ImportError as e2:
        print(f"❌ Failed to import production_app: {e2}")
        raise e2

# Make sure the app is configured for production
if hasattr(app, 'config'):
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting RABuddy on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
