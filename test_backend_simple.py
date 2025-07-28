#!/usr/bin/env python3
"""
Simple test script for RABuddy backend
"""

import sys
import os
from pathlib import Path

# Add backend paths
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir / "src"))
sys.path.insert(0, str(backend_dir))

from flask import Flask
from flask_cors import CORS

def create_simple_test_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)
    
    # Simple CORS - allow everything
    CORS(app, origins="*", 
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])
    
    @app.route('/')
    def home():
        return {"message": "RABuddy backend is running!", "status": "OK"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy"}
    
    @app.route('/api/test', methods=['GET', 'POST'])
    def test():
        return {
            "message": "API test successful",
            "method": "GET" if hasattr(test, '__name__') else "POST",
            "status": "working"
        }
    
    @app.route('/api/query', methods=['POST', 'OPTIONS'])
    def query():
        from flask import request, jsonify
        
        if request.method == 'OPTIONS':
            response = jsonify({'message': 'CORS preflight OK'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
        
        data = request.get_json() if request.is_json else {}
        question = data.get('question', 'No question provided')
        
        return jsonify({
            "answer": f"Test response for: {question}",
            "sources": [],
            "session_id": "test-session",
            "query_id": "test-123",
            "status": "success"
        })
    
    @app.route('/api/status')
    def status():
        return {"status": "online", "message": "Backend is working"}
    
    return app

if __name__ == '__main__':
    print("🧪 Starting simple RABuddy test backend...")
    app = create_simple_test_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
