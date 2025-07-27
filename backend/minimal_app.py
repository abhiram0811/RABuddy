#!/usr/bin/env python3
"""
Minimal working RABuddy backend
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
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "*"], 
     methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Global variables for lazy loading
rag_engine = None
feedback_logger = None

def get_rag_engine():
    """Lazy load RAG engine"""
    global rag_engine
    if rag_engine is None:
        try:
            # Try importing from src or backend directory
            try:
                from src.rag_engine import RAGEngine
            except ImportError:
                from src.rag_engine import RAGEngine
            rag_engine = RAGEngine()
            logger.info("✅ RAG engine loaded")
        except Exception as e:
            logger.error(f"❌ Error loading RAG engine: {e}")
            rag_engine = False  # Mark as failed
    return rag_engine if rag_engine is not False else None

@app.route('/health')
def health():
    return {"status": "healthy", "service": "RABuddy Backend"}

@app.route('/api/status')
def status():
    """Get system status"""
    try:
        engine = get_rag_engine()
        if engine:
            return jsonify(engine.get_status())
        else:
            return jsonify({"status": "error", "message": "RAG engine failed to load"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Simple test endpoint for frontend debugging"""
    return jsonify({
        "message": "Backend is working!",
        "timestamp": datetime.now().isoformat(),
        "method": request.method
    })

@app.route('/api/query', methods=['POST'])
def query():
    """Process RAG query"""
    try:
        logger.info(f"Received query request from {request.remote_addr}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        engine = get_rag_engine()
        if not engine:
            logger.error("RAG engine not available")
            return jsonify({"error": "RAG engine not available"}), 500
        
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'question' not in data:
            logger.error("Missing question in request")
            return jsonify({"error": "Missing question"}), 400
        
        logger.info(f"Processing question: {data['question']}")
        # Call with proper parameters (question, top_k)
        result = engine.query(data['question'])
        logger.info(f"Query result keys: {result.keys()}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Log feedback"""
    try:
        data = request.get_json()
        # For now, just log to console since Supabase table might not exist
        logger.info(f"Feedback received: {data}")
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
    return {"routes": routes}

if __name__ == '__main__':
    logger.info("🚀 Starting minimal RABuddy backend...")
    app.run(debug=True, host='0.0.0.0', port=5001)
