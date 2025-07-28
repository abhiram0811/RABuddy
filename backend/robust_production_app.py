#!/usr/bin/env python3
"""
RABuddy Production Backend with Full RAG Capabilities
Based on the working minimal app structure but with full RAG functionality
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
import traceback

# Add paths for imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

app = Flask(__name__)

# Simple CORS configuration that works
CORS(app, origins="*", 
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Global variables for lazy loading
rag_engine = None
pdf_processor = None

def get_rag_engine():
    """Lazy load RAG engine"""
    global rag_engine
    if rag_engine is None:
        try:
            from src.rag_engine import RAGEngine
            rag_engine = RAGEngine()
            print("✅ RAG engine loaded successfully")
        except Exception as e:
            print(f"❌ Error loading RAG engine: {e}")
            print(f"Traceback: {traceback.format_exc()}")
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
    return {
        "message": "RABuddy Production Backend with RAG", 
        "status": "running",
        "version": "2.0.0",
        "features": ["RAG", "PDF Processing", "CORS", "Production Ready"]
    }

@app.route('/health')
def health():
    return {
        "status": "healthy", 
        "service": "RABuddy Production",
        "rag_available": get_rag_engine() is not None,
        "pdf_available": get_pdf_processor() is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get detailed system status"""
    rag = get_rag_engine()
    pdf = get_pdf_processor()
    
    return jsonify({
        "status": "online",
        "message": "RABuddy Production API",
        "environment": "production",
        "components": {
            "rag_engine": "loaded" if rag else "error",
            "pdf_processor": "loaded" if pdf else "error"
        },
        "endpoints": [
            "/api/query - POST - Ask questions",
            "/api/feedback - POST - Submit feedback", 
            "/api/status - GET - System status",
            "/health - GET - Health check"
        ]
    })

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    """Test endpoint"""
    return jsonify({
        "message": "RABuddy Production API test successful",
        "method": request.method,
        "status": "working",
        "rag_ready": get_rag_engine() is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    """Process user queries with RAG"""
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
        
        # Try to use RAG engine
        rag = get_rag_engine()
        if rag:
            try:
                result = rag.query(question)
                return jsonify({
                    "answer": result.get("answer", "No answer generated"),
                    "sources": result.get("sources", []),
                    "session_id": result.get("session_id", str(uuid.uuid4())),
                    "query_id": result.get("query_id", str(uuid.uuid4())),
                    "status": "success",
                    "mode": "rag"
                })
            except Exception as e:
                print(f"RAG engine error: {e}")
                # Fall back to simple response
                pass
        
        # Fallback response when RAG is not available
        return jsonify({
            "answer": f"I received your question: '{question}'. The RAG system is currently initializing. Please try again in a moment, or this could be a test response while the system loads.",
            "sources": [],
            "session_id": str(uuid.uuid4()),
            "query_id": str(uuid.uuid4()),
            "status": "success", 
            "mode": "fallback"
        })
        
    except Exception as e:
        print(f"Query endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error", 
            "details": str(e) if os.getenv('DEBUG') else None
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
        
        # Log feedback (could be enhanced to save to database)
        print(f"📝 Feedback received: {data}")
        
        return jsonify({
            "message": "Feedback received successfully",
            "feedback_id": feedback_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Feedback endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/build-rag', methods=['POST'])
def build_rag():
    """Rebuild RAG index from PDFs"""
    try:
        # Try to rebuild RAG
        pdf = get_pdf_processor()
        if pdf:
            # Process PDFs and rebuild index
            result = pdf.process_all_pdfs()
            return jsonify({
                "message": "RAG index rebuilt successfully", 
                "result": result,
                "status": "success"
            })
        else:
            return jsonify({"error": "PDF processor not available"}), 500
            
    except Exception as e:
        print(f"Build RAG error: {e}")
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

@app.route('/debug/system')
def debug_system():
    """Debug system information"""
    return {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "python_path": sys.path[:5],  # First 5 entries
        "environment_vars": {k: v for k, v in os.environ.items() if k.startswith(('FLASK', 'PORT', 'RENDER'))},
        "rag_engine": "loaded" if get_rag_engine() else "not loaded",
        "pdf_processor": "loaded" if get_pdf_processor() else "not loaded"
    }

# Initialize system components on startup
def initialize_system():
    """Initialize system components"""
    print("🚀 Initializing RABuddy Production System...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Try to load components
    rag = get_rag_engine()
    pdf = get_pdf_processor()
    
    print(f"RAG Engine: {'✅ Loaded' if rag else '❌ Not available'}")
    print(f"PDF Processor: {'✅ Loaded' if pdf else '❌ Not available'}")
    print("📡 RABuddy Production System Ready!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting RABuddy Production Backend on port {port}")
    
    # Initialize system
    initialize_system()
    
    app.run(debug=False, host='0.0.0.0', port=port)
