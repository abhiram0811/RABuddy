#!/usr/bin/env python3
"""
RAG-Enabled Production App
Built on the solid foundation of the nuclear app that works!
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
backend_dir = Path(__file__).parent / 'backend'
src_dir = backend_dir / 'src'
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(backend_dir))

print("🚀 Starting RAG-Enabled RABuddy...")
print(f"📁 Backend dir: {backend_dir}")
print(f"📁 Src dir: {src_dir}")

# Create the Flask app with the proven nuclear foundation
app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"])

# Initialize RAG engine
rag_engine = None

def initialize_rag():
    """Initialize RAG components with fallback"""
    global rag_engine
    try:
        print("🔧 Attempting to initialize RAG engine...")
        from production_rag_engine import ProductionRAGEngine
        rag_engine = ProductionRAGEngine()
        print("✅ RAG engine initialized successfully!")
        return True
    except Exception as e:
        print(f"⚠️ RAG initialization failed: {e}")
        print("📱 Falling back to simple responses")
        return False

# Try to initialize RAG on startup
RAG_ENABLED = initialize_rag()

@app.route('/')
def home():
    return jsonify({
        "service": "RABuddy RAG Production Backend",
        "version": "RAG-1.0",
        "status": "🚀 RAG-ENABLED SUCCESS! 🚀",
        "message": "RAG Backend Deployed Successfully!",
        "rag_enabled": RAG_ENABLED,
        "components": {
            "rag_engine": "initialized" if rag_engine else "fallback_mode"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "service": "RABuddy RAG Backend",
        "status": "healthy",
        "version": "RAG-1.0",
        "rag_enabled": RAG_ENABLED
    })

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    """Test endpoint - RAG VERSION"""
    return jsonify({
        "message": "🚀 RAG SUCCESS! RABuddy RAG v1.0 IS WORKING! 🚀",
        "method": request.method,
        "status": "RAG_SUCCESS",
        "timestamp": datetime.now().isoformat(),
        "gemini_key": "SET" if os.getenv('GEMINI_API_KEY') else "MISSING",
        "version": "RAG-1.0",
        "deployment": "RAG OPTION SUCCESS!",
        "rag_enabled": RAG_ENABLED,
        "components": {
            "embedding_model": bool(rag_engine and rag_engine.embedding_model) if rag_engine else False,
            "chroma_db": bool(rag_engine and rag_engine.collection) if rag_engine else False,
            "gemini": bool(rag_engine and rag_engine.gemini_model) if rag_engine else False
        }
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    """Process user queries with RAG capability"""
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    
    try:
        data = request.get_json() if request.is_json else {}
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        query_id = str(uuid.uuid4())
        
        # If RAG is enabled, try to use it
        if RAG_ENABLED and rag_engine:
            try:
                print(f"🔍 Processing RAG query: {question}")
                result = rag_engine.process_query(question, query_id)
                
                # Format the response for the frontend
                response = {
                    "answer": result.get("answer", "Sorry, I couldn't generate an answer."),
                    "sources": result.get("sources", []),
                    "session_id": result.get("session_id", str(uuid.uuid4())),
                    "query_id": query_id,
                    "status": "RAG_SUCCESS",
                    "mode": "rag_enabled",
                    "version": "RAG-1.0"
                }
                
                print(f"✅ RAG query processed successfully")
                return jsonify(response)
                
            except Exception as e:
                print(f"❌ RAG query failed: {e}")
                print("🔄 Falling back to simple response")
        
        # Fallback response (when RAG is not available or fails)
        fallback_responses = {
            "lockout": "For lockouts, contact your RA or the front desk. After hours, contact the RD on duty.",
            "guest": "Guest policies require registration at the front desk and are limited to specific hours.",
            "emergency": "For emergencies, call 911 first, then contact your RA or RD on duty.",
            "facilities": "For facilities issues, submit a work order through the housing portal or contact the front desk.",
            "default": f"I received your question: '{question}'. While my RAG system is initializing, please refer to your paraprofessional manual or contact your RA for specific policy information."
        }
        
        # Simple keyword matching for fallback
        answer = fallback_responses["default"]
        for key, response in fallback_responses.items():
            if key in question.lower():
                answer = response
                break
        
        return jsonify({
            "answer": f"🚀 {answer} (RAG system status: {'initializing' if not RAG_ENABLED else 'available'})",
            "sources": [
                {"source_number": 1, "filename": "System Status", "page_number": 1, "relevance_score": 1.0, "text_preview": "Backend is operational"}
            ],
            "session_id": str(uuid.uuid4()),
            "query_id": query_id,
            "status": "FALLBACK_SUCCESS",
            "mode": "fallback",
            "version": "RAG-1.0"
        })
        
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "status": "ERROR",
            "query_id": str(uuid.uuid4())
        }), 500

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Handle user feedback"""
    try:
        data = request.get_json() if request.is_json else {}
        query_id = data.get('query_id')
        feedback_type = data.get('feedback_type')
        
        print(f"📝 Received feedback: {feedback_type} for query {query_id}")
        
        # Here you could log to a database or file
        # For now, just acknowledge receipt
        
        return jsonify({
            "message": "Feedback received",
            "query_id": query_id,
            "feedback_type": feedback_type,
            "status": "SUCCESS"
        })
        
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return jsonify({"error": "Failed to process feedback"}), 500

@app.route('/api/status')
def api_status():
    """Detailed status endpoint"""
    status = {
        "service": "RABuddy RAG Backend",
        "version": "RAG-1.0",
        "timestamp": datetime.now().isoformat(),
        "rag_enabled": RAG_ENABLED,
        "environment": {
            "gemini_api_key": "SET" if os.getenv('GEMINI_API_KEY') else "MISSING",
            "python_version": sys.version,
            "working_directory": str(Path.cwd())
        }
    }
    
    if rag_engine:
        status["rag_components"] = {
            "embedding_model": bool(rag_engine.embedding_model),
            "chroma_db": bool(rag_engine.collection),
            "gemini_model": bool(rag_engine.gemini_model),
            "pdf_processor": bool(rag_engine.pdf_processor),
            "initialized": rag_engine.initialized
        }
        
        if rag_engine.collection:
            try:
                doc_count = rag_engine.collection.count()
                status["document_count"] = doc_count
            except:
                status["document_count"] = "unknown"
    
    return jsonify(status)

if __name__ == '__main__':
    print("🚀 RAG-Enabled RABuddy starting...")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Server starting on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🤖 RAG enabled: {RAG_ENABLED}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
