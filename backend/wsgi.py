#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
GUARANTEED RAG APP - v5.0
"""
import os
import sys
from pathlib import Path

# Simple path setup
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print(f"🚀🔥 WSGI Starting - GUARANTEED RAG App v5.0 🔥🚀")
print(f"📁 Backend dir: {backend_dir}")

# Import the GUARANTEED RAG app first
try:
    from guaranteed_rag_app import app
    print("✅🔥 Successfully imported guaranteed_rag_app! 🔥✅")
except ImportError as e:
    print(f"❌ Failed to import guaranteed_rag_app: {e}")
    
    # Fallback to production RAG app
    try:
        from production_rag_app import app
        print("✅ Fallback: Successfully imported production_rag_app")
    except ImportError as e2:
        print(f"❌ Failed to import production_rag_app: {e2}")
        
        # Fallback to nuclear app
        try:
            print("🔄 Falling back to nuclear_app...")
            # Go up one level to access nuclear_app.py
            root_dir = backend_dir.parent
            sys.path.insert(0, str(root_dir))
            from nuclear_app import app
            print("✅ Successfully imported nuclear_app as fallback")
        except ImportError as e3:
            print(f"❌ Failed to import nuclear_app: {e3}")
            # Last resort - create minimal app
            from flask import Flask
            app = Flask(__name__)
            @app.route('/')
            def home():
                return {"status": "WSGI fallback active", "error": str(e)}
            print("⚠️ Using minimal fallback app")

# Make sure the app is configured for production
if hasattr(app, 'config'):
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀🔥 Starting GUARANTEED RAG app on port {port} 🔥🚀")
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting RABuddy on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
