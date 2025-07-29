#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
GUARANTEED RAG APP ONLY - NO FALLBACKS!
"""
import os
import sys
from pathlib import Path

# Simple path setup
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print(f"🚀🔥 WSGI Starting - GUARANTEED RAG ONLY! 🔥🚀")
print(f"📁 Backend dir: {backend_dir}")

# Import ONLY the GUARANTEED RAG app - NO FALLBACKS!
from guaranteed_rag_app import app
print("✅🔥 GUARANTEED RAG APP LOADED - NO NUCLEAR FALLBACK! �✅")

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
