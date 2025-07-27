from flask import Blueprint, request, jsonify
from loguru import logger
import traceback
from rag_engine import RAGEngine
from feedback_logger import FeedbackLogger

# Initialize blueprint
api_bp = Blueprint('api', __name__)

# Initialize components
rag_engine = RAGEngine()
feedback_logger = FeedbackLogger()

@api_bp.route('/query', methods=['POST'])
def handle_query():
    """Handle user questions and return AI-generated answers with sources"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        
        logger.info(f"Processing query: {question}")
        
        # Get answer from RAG engine
        result = rag_engine.query(question)
        
        logger.info(f"Query processed successfully for: {question}")
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
            "query_id": result["query_id"]
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/feedback', methods=['POST'])
def handle_feedback():
    """Log user feedback for answers"""
    try:
        data = request.get_json()
        required_fields = ['query_id', 'feedback_type']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "query_id and feedback_type are required"}), 400
        
        query_id = data['query_id']
        feedback_type = data['feedback_type']  # 'positive' or 'negative'
        comment = data.get('comment', '')
        
        if feedback_type not in ['positive', 'negative']:
            return jsonify({"error": "feedback_type must be 'positive' or 'negative'"}), 400
        
        logger.info(f"Logging feedback: {feedback_type} for query {query_id}")
        
        # Log feedback
        feedback_logger.log_feedback(query_id, feedback_type, comment)
        
        return jsonify({"message": "Feedback logged successfully"})
        
    except Exception as e:
        logger.error(f"Error logging feedback: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status and statistics"""
    try:
        status = rag_engine.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
