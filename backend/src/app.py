from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from loguru import logger
from pathlib import Path

# Load environment variables
load_dotenv()

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Import config after Flask initialization
    from config import get_config, CORS_ORIGINS
    
    # Apply configuration
    if config:
        app_config = config
    else:
        app_config = get_config()
    
    for key, value in app_config.items():
        app.config[key] = value
    
    # Configure CORS for cloud deployment
    CORS(app, origins=CORS_ORIGINS, 
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "OPTIONS"])
    
    # Setup logging (simplified for cloud)
    if app_config.get('ENVIRONMENT') == 'production':
        logger.remove()  # Remove default handler
        logger.add(lambda msg: print(msg, end=""), level="INFO")
    else:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        logger.add(logs_dir / "rabuddy.log", rotation="10 MB", retention="7 days")
    
    logger.info("🌐 RABuddy application starting up")
    logger.info(f"🔧 Environment: {app_config.get('ENVIRONMENT', 'development')}")
    
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
