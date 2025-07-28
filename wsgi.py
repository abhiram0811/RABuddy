#!/usr/bin/env python3
"""
Root WSGI entry point for Render deployment
Using robust production app with full RAG capabilities - v3.0
"""
import os
import sys
from pathlib import Path

# Setup paths
root_dir = Path(__file__).parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(root_dir))

print(f"🔧 WSGI Setup - Root: {root_dir}")
print(f"🔧 WSGI Setup - Backend: {backend_dir}")
print(f"🔧 Python path: {sys.path[:3]}")

# Import the robust production app with full RAG
try:
    # Change to backend directory for proper imports
    os.chdir(backend_dir)
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
        try:
            # Try the modular app as last resort
            from backend.src.app import create_app
            from backend.src.config import get_config
            config = get_config()
            config.update({
                'ENVIRONMENT': 'production',
                'DEBUG': False,
            })
            app = create_app(config)
            print("✅ Last resort: Using modular app")
        except Exception as e3:
            print(f"❌ All imports failed: {e3}")
            raise e3

# Make sure the app is configured for production
if hasattr(app, 'config'):
    app.config['DEBUG'] = False
    app.config['TESTING'] = False

# Add environment variables info endpoint for debugging
@app.route('/debug/env')
def debug_env():
    return {
        'working_directory': os.getcwd(),
        'python_path': sys.path[:5],
        'environment_vars': {
            'PORT': os.environ.get('PORT'),
            'GEMINI_API_KEY': 'SET' if os.environ.get('GEMINI_API_KEY') else 'MISSING',
            'FLASK_ENV': os.environ.get('FLASK_ENV'),
            'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting RABuddy on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
