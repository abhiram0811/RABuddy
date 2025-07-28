#!/usr/bin/env python3
"""
Minimal RABuddy backend for debugging Render deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)

# Simple CORS - allow everything for testing
CORS(app, origins="*")

@app.route('/')
def home():
    return {"message": "RABuddy Minimal Backend", "status": "running"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "RABuddy Minimal"}

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        "status": "online",
        "message": "Minimal API is working",
        "environment": "production"
    })

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    return jsonify({
        "message": "Minimal API test successful",
        "method": request.method,
        "status": "working"
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    try:
        data = request.get_json() if request.is_json else {}
        question = data.get('question', 'No question provided')
        
        return jsonify({
            "answer": f"Minimal backend response: {question}",
            "sources": [],
            "session_id": "minimal-session",
            "query_id": "minimal-123",
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/routes')
def debug_routes():
    """List all routes for debugging"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "url": str(rule)
        })
    return {"routes": routes}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting minimal backend on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
