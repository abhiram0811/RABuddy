from flask import Blueprint, request, jsonify
from loguru import logger
import traceback

# Initialize blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/query', methods=['POST'])
def handle_query():
    """Handle user questions - simplified version for testing"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        # Temporary response until we get the full RAG engine working
        return jsonify({
            "answer": "Backend is working! Your question: " + data['question'],
            "sources": [],
            "session_id": "test-session"
        })
        
    except Exception as e:
        logger.error(f"Error in /query endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/feedback', methods=['POST'])
def handle_feedback():
    """Handle user feedback - simplified version"""
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
