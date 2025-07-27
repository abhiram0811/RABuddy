#!/usr/bin/env python3
"""
RABuddy backend for public access with enhanced security
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add paths
current_dir = Path(__file__).parent
backend_dir = current_dir
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(backend_dir))

# Load environment
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Enhanced CORS for public access
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://localhost:3002", 
    "http://localhost:3003",
    "https://*.ngrok.io",
    "https://*.loca.lt",
    "https://*.cloudflare.com"
]

# Get additional allowed origins from environment
extra_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if extra_origins and extra_origins[0]:
    allowed_origins.extend([origin.strip() for origin in extra_origins])

CORS(app, 
     origins=allowed_origins + ["*"],  # Allow all for development
     methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True)

# Global variables for lazy loading
rag_engine = None

def get_rag_engine():
    """Lazy load RAG engine"""
    global rag_engine
    if rag_engine is None:
        try:
            from src.rag_engine import RAGEngine
            rag_engine = RAGEngine()
            logger.info("✅ RAG engine loaded")
        except Exception as e:
            logger.error(f"❌ Error loading RAG engine: {e}")
            rag_engine = False
    return rag_engine if rag_engine is not False else None

@app.route('/health')
def health():
    return {"status": "healthy", "service": "RABuddy Backend", "public": True}

@app.route('/api/status')
def status():
    """Get system status"""
    try:
        engine = get_rag_engine()
        if engine:
            status_info = engine.get_status()
            status_info["public_access"] = True
            status_info["cors_enabled"] = True
            return jsonify(status_info)
        else:
            return jsonify({"status": "error", "message": "RAG engine failed to load"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint with origin info"""
    origin = request.headers.get('Origin', 'Unknown')
    return jsonify({
        "message": "RABuddy backend is working publicly!",
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "origin": origin,
        "public_access": True
    })

@app.route('/api/query', methods=['POST'])
def query():
    """Process RAG query with request logging"""
    try:
        origin = request.headers.get('Origin', 'Unknown')
        logger.info(f"Public query from origin: {origin}")
        
        engine = get_rag_engine()
        if not engine:
            logger.error("RAG engine not available")
            return jsonify({"error": "RAG engine not available"}), 500
        
        data = request.get_json()
        if not data or 'question' not in data:
            logger.error("Missing question in request")
            return jsonify({"error": "Missing question"}), 400
        
        logger.info(f"Processing public query: {data['question']}")
        result = engine.query(data['question'])
        
        # Add public access indicator
        result["public_access"] = True
        result["origin"] = origin
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Public query error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Log feedback with origin tracking"""
    try:
        data = request.get_json()
        origin = request.headers.get('Origin', 'Unknown')
        
        # Add origin to feedback data
        if data:
            data["origin"] = origin
            data["public_access"] = True
        
        logger.info(f"Public feedback received from {origin}: {data}")
        return jsonify({"success": True, "feedback_id": str(uuid.uuid4())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/routes')
def debug_routes():
    """Debug endpoint to list all routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "url": str(rule)
        })
    return {"routes": routes, "public_access": True}

if __name__ == '__main__':
    logger.info("🌐 Starting RABuddy backend for PUBLIC ACCESS...")
    logger.info("🔒 CORS configured for public tunnels")
    app.run(debug=True, host='0.0.0.0', port=5001)
