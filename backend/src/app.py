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
        from routes_simple import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        logger.info("✅ Simplified API blueprint registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering API blueprint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fallback: Add routes directly to app
        @app.route('/api/query', methods=['POST'])
        def handle_query():
            """Handle user questions - direct route fallback"""
            try:
                from flask import request, jsonify
                data = request.get_json()
                if not data or 'question' not in data:
                    return jsonify({"error": "Question is required"}), 400
                
                return jsonify({
                    "answer": "Backend is working! Your question: " + data['question'],
                    "sources": [],
                    "session_id": "test-session"
                })
                
            except Exception as e:
                logger.error(f"Error in /query endpoint: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @app.route('/api/feedback', methods=['POST'])
        def handle_feedback():
            """Handle user feedback - direct route"""
            try:
                from flask import request, jsonify
                data = request.get_json()
                logger.info(f"Feedback received: {data}")
                return jsonify({"message": "Feedback received"}), 200
                
            except Exception as e:
                logger.error(f"Error in /feedback endpoint: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @app.route('/api/status', methods=['GET'])
        def get_status():
            """Get API status"""
            from flask import jsonify
            return jsonify({
                "status": "online", 
                "message": "RABuddy API is running"
            })
            
        logger.info("✅ Direct API routes registered as fallback")
    
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
