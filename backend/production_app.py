#!/usr/bin/env python3
"""
Production RABuddy backend with full RAG capabilities for Render deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from pathlib import Path
import uuid
from datetime import datetime
import traceback

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

app = Flask(__name__)

# Simple CORS - allow everything for production
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"])

# Global variables for lazy loading
rag_engine = None
pdf_processor = None

def get_rag_engine():
    """Lazy load RAG engine to avoid startup errors"""
    global rag_engine
    if rag_engine is None:
        try:
            from src.production_rag_engine import ProductionRAGEngine
            rag_engine = ProductionRAGEngine()
            print("✅ Production RAG engine loaded successfully")
        except Exception as e:
            print(f"❌ Error loading RAG engine: {e}")
            rag_engine = False
    return rag_engine if rag_engine is not False else None

def get_pdf_processor():
    """Lazy load PDF processor"""
    global pdf_processor
    if pdf_processor is None:
        try:
            from src.pdf_processor import PDFProcessor
            pdf_processor = PDFProcessor()
            print("✅ PDF processor loaded successfully")
        except Exception as e:
            print(f"❌ Error loading PDF processor: {e}")
            pdf_processor = False
    return pdf_processor if pdf_processor is not False else None

@app.route('/')
def home():
    return {"message": "RABuddy Production Backend", "status": "running", "version": "2.0"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "RABuddy Production"}

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get detailed system status"""
    try:
        rag = get_rag_engine()
        pdf = get_pdf_processor()
        
        status = {
            "status": "online",
            "message": "RABuddy Production API",
            "environment": "production",
            "components": {
                "rag_engine": "loaded" if rag else "failed",
                "pdf_processor": "loaded" if pdf else "failed",
                "document_count": 0
            },
            "endpoints": [
                "/api/query - POST - Ask questions",
                "/api/feedback - POST - Submit feedback", 
                "/api/status - GET - System status",
                "/api/documents - GET - Document info",
                "/health - GET - Health check"
            ]
        }
        
        if rag and hasattr(rag, 'collection'):
            try:
                status["components"]["document_count"] = rag.collection.count()
            except:
                status["components"]["document_count"] = "unknown"
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "components": {"rag_engine": "failed", "pdf_processor": "failed"}
        })

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    return jsonify({
        "message": "RABuddy Production API test successful",
        "method": request.method,
        "status": "working",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    """Handle user questions with full RAG capabilities"""
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
        
        # Try to use RAG engine
        rag = get_rag_engine()
        if rag:
            try:
                print(f"🔍 Processing RAG query: {question}")
                result = rag.query(question)
                
                # Ensure proper response format
                response = {
                    "answer": result.get("answer", "No answer generated"),
                    "sources": result.get("sources", []),
                    "session_id": result.get("session_id", "rag-session"),
                    "query_id": query_id,
                    "status": "success",
                    "engine": "rag"
                }
                
                print(f"✅ RAG query successful: {query_id}")
                return jsonify(response)
                
            except Exception as e:
                print(f"❌ RAG query failed: {e}")
                # Fall back to simple response
                pass
        
        # Fallback response if RAG fails
        response = {
            "answer": f"I received your question: '{question}'. The RAG system is currently initializing. Please try again in a moment, or this may be a simple acknowledgment while the full system loads.",
            "sources": [],
            "session_id": "fallback-session",
            "query_id": query_id,
            "status": "fallback",
            "engine": "simple"
        }
        
        return jsonify(response)
        
    except Exception as e:
        error_id = str(uuid.uuid4())
        print(f"❌ Query error {error_id}: {e}")
        traceback.print_exc()
        
        return jsonify({
            "error": "Internal server error",
            "error_id": error_id,
            "query_id": str(uuid.uuid4())
        }), 500

@app.route('/api/feedback', methods=['POST', 'OPTIONS'])
def api_feedback():
    """Handle user feedback"""
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'CORS preflight OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        data = request.get_json() if request.is_json else {}
        feedback_id = str(uuid.uuid4())
        
        print(f"📝 Feedback received {feedback_id}: {data}")
        
        return jsonify({
            "message": "Feedback received successfully",
            "feedback_id": feedback_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/documents', methods=['GET'])
def api_documents():
    """Get information about loaded documents"""
    try:
        rag = get_rag_engine()
        if not rag:
            return jsonify({
                "status": "rag_not_loaded",
                "documents": [],
                "count": 0
            })
        
        # Try to get document info
        doc_count = 0
        if hasattr(rag, 'collection'):
            try:
                doc_count = rag.collection.count()
            except:
                pass
        
        return jsonify({
            "status": "loaded",
            "count": doc_count,
            "message": f"{doc_count} document chunks loaded"
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
    return {"routes": routes, "count": len(routes)}

# Initialize on startup (but don't fail if it doesn't work)
def initialize_system():
    """Initialize system components on startup"""
    print("🚀 Initializing RABuddy production system...")
    
    # Try to load components
    rag = get_rag_engine()
    pdf = get_pdf_processor()
    
    print(f"RAG Engine: {'✅' if rag else '❌'}")
    print(f"PDF Processor: {'✅' if pdf else '❌'}")
    print("📡 RABuddy production system ready!")

# Call initialization when app starts
with app.app_context():
    initialize_system()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting RABuddy Production Backend on port {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🔧 Python path: {sys.path}")
    
    app.run(debug=False, host='0.0.0.0', port=port)
