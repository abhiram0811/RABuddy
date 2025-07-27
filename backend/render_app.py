import os
import sys
import logging
from pathlib import Path
from loguru import logger

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))

# Import after path setup
from src.app import create_app
from src.config import get_config

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")

def create_render_app():
    """Create Flask app configured for Render deployment"""
    try:
        # Get configuration
        config = get_config()
        
        # Override settings for Render
        config.update({
            'ENVIRONMENT': 'production',
            'DEBUG': False,
            'HOST': '0.0.0.0',
            'PORT': int(os.environ.get('PORT', 10000)),  # Render uses PORT env var
            'CORS_ORIGINS': ['*'],  # Allow all origins for public access
        })
        
        # Create the Flask app
        app = create_app(config)
        
        # Add health check endpoint required by Render
        @app.route('/health')
        def health_check():
            return {'status': 'healthy', 'service': 'RABuddy Backend'}, 200
            
        # Add render-specific endpoint info
        @app.route('/api/info')
        def api_info():
            return {
                'service': 'RABuddy Backend',
                'version': '1.0.0',
                'environment': 'production',
                'endpoints': [
                    '/api/query',
                    '/api/feedback', 
                    '/api/status',
                    '/health'
                ]
            }, 200
        
        logger.info("🌐 RABuddy backend configured for Render deployment")
        logger.info(f"🔒 CORS configured for public access")
        logger.info(f"🚀 Ready to serve on port {config['PORT']}")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create app: {str(e)}")
        raise

# Create the Flask app instance
app = create_render_app()

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
