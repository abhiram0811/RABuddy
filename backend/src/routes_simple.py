from flask import Blueprint, request, jsonify
from loguru import logger
import traceback

# Initialize blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        "message": "RABuddy API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Ask questions about CSU housing policies",
            "POST /feedback": "Submit feedback for answers",
            "GET /status": "Check API status"
        }
    })

@api_bp.route('/query', methods=['POST', 'OPTIONS'])
def handle_query():
    """Handle user questions - simplified version for testing"""
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        # Temporary response until we get the full RAG engine working
        return jsonify({
            "answer": f"Backend is working! Your question: {data['question']}. This is a test response while we fix the RAG engine.",
            "sources": [],
            "session_id": "test-session",
            "query_id": "test-query-123"
        })
        
    except Exception as e:
        logger.error(f"Error in /query endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/feedback', methods=['POST', 'OPTIONS'])
def handle_feedback():
    """Handle user feedback - simplified version"""
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        logger.info(f"Feedback received: {data}")
        return jsonify({"message": "Feedback received"}), 200
        
    except Exception as e:
        logger.error(f"Error in /feedback endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({
        "status": "online",
        "message": "RABuddy API is running"
    })
