from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from loguru import logger

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins=["http://localhost:3000", "https://*.vercel.app"])
    
    # Configure Flask
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    
    # Setup logging
    logger.add("logs/rabuddy.log", rotation="10 MB", retention="7 days")
    logger.info("RABuddy application starting up")
    
    # Register blueprints
    try:
        from routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        logger.info("✅ API blueprint registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering API blueprint: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    @app.route('/')
    def home():
        return {"message": "RABuddy Backend API", "status": "running"}
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "RABuddy Backend"}
    
    # Simple test API endpoint
    @app.route('/api/test')
    def test_api():
        return {"message": "API is working", "status": "success"}
    
    # List all routes for debugging
    @app.route('/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "url": str(rule)
            })
        return {"routes": routes}
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("🚀 Starting RABuddy Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
