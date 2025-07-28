#!/usr/bin/env python3
"""
Root WSGI entry point for Render deployment
Using DEFINITIVE production app with full RAG capabilities - v4.0
"""
import os
import sys
from pathlib import Path

# Setup paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print(f"🔧 WSGI Setup v4.0 - Root: {root_dir}")
print(f"🔧 Python path: {sys.path[:3]}")

# Import the DEFINITIVE production app
try:
    from definitive_production_app import app
    print("✅ Successfully imported definitive_production_app v4.0")
except ImportError as e:
    print(f"❌ Failed to import definitive_production_app: {e}")
    raise e

# Make sure the app is configured for production
if hasattr(app, 'config'):
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

print("🚀 WSGI v4.0 ready to serve requests!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting RABuddy DEFINITIVE v4.0 on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
