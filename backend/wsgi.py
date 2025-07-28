#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
Using RAG-enabled app built on nuclear foundation - v3.0
"""
import os
import sys
from pathlib import Path

# Simple path setup - go up one level to access rag_app.py
backend_dir = Path(__file__).parent
root_dir = backend_dir.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

print(f"🚀 WSGI Starting - RAG App v3.0")
print(f"📁 Backend dir: {backend_dir}")
print(f"📁 Root dir: {root_dir}")

# Import the RAG-enabled app
try:
    from rag_app import app
    print("✅ Successfully imported rag_app")
except ImportError as e:
    print(f"❌ Failed to import rag_app: {e}")
    print("🔄 Falling back to nuclear_app...")
    try:
        sys.path.insert(0, str(root_dir))
        from nuclear_app import app
        print("✅ Successfully imported nuclear_app as fallback")
    except ImportError as e2:
        print(f"❌ Failed to import nuclear_app: {e2}")
        # Last resort - create minimal app
        from flask import Flask
        app = Flask(__name__)
        @app.route('/')
        def home():
            return {"status": "WSGI fallback active", "error": str(e)}
        print("⚠️ Using minimal fallback app")
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
