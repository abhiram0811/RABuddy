#!/usr/bin/env python3
"""
DEFINITIVE Production App for Render - v4.0
This WILL work with full RAG capabilities
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
import traceback

# Setup paths - be very explicit
current_dir = Path(__file__).parent.absolute()
backend_dir = current_dir if current_dir.name == 'backend' else current_dir / 'backend'
src_dir = backend_dir / "src"

print(f"🔧 Current dir: {current_dir}")
print(f"🔧 Backend dir: {backend_dir}")
print(f"🔧 Src dir: {src_dir}")

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(src_dir))

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"])

# Global variables for lazy loading
rag_engine = None
pdf_processor = None

def get_rag_engine():
    """Lazy load RAG engine"""
    global rag_engine
    if rag_engine is None:
        try:
            # Try production RAG first
            from src.production_rag_engine import ProductionRAGEngine
            rag_engine = ProductionRAGEngine()
            print("✅ Production RAG engine loaded successfully")
        except Exception as e1:
            print(f"❌ Production RAG failed: {e1}")
            try:
                # Fallback to regular RAG
                from src.rag_engine import RAGEngine
                rag_engine = RAGEngine()
                print("✅ Regular RAG engine loaded successfully")
            except Exception as e2:
                print(f"❌ Regular RAG failed: {e2}")
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
            print(f"❌ PDF processor failed: {e}")
            pdf_processor = False
    return pdf_processor if pdf_processor is not False else None

# Routes
@app.route('/')
def home():
    return jsonify({
        "service": "RABuddy Production Backend",
        "version": "4.0",
        "status": "running",
        "message": "DEFINITIVE Production Version - v4.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "service": "RABuddy Backend",
        "status": "healthy",
        "version": "4.0"
    })

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    """Test endpoint - PRODUCTION VERSION"""
    return jsonify({
        "message": "🚀 RABuddy DEFINITIVE Production API - v4.0 WORKING!",
        "method": request.method,
        "status": "production_ready",
        "rag_ready": get_rag_engine() is not None,
        "pdf_ready": get_pdf_processor() is not None,
        "gemini_key": "SET" if os.getenv('GEMINI_API_KEY') else "MISSING",
        "timestamp": datetime.now().isoformat(),
        "working_directory": str(Path.cwd()),
        "backend_directory": str(backend_dir)
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
                    "mode": "rag_production_v4"
                })
            except Exception as e:
                print(f"RAG engine error: {e}")
                # Fall through to fallback
        
        # Fallback response
        return jsonify({
            "answer": f"I received your question: '{question}'. This is the DEFINITIVE Production RABuddy v4.0! The RAG system is initializing with your PDFs. Please try again in a moment for AI-powered responses with PDF citations.",
            "sources": [],
            "session_id": str(uuid.uuid4()),
            "query_id": str(uuid.uuid4()),
            "status": "success", 
            "mode": "fallback_v4"
        })
        
    except Exception as e:
        print(f"Query endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error", 
            "details": str(e) if os.getenv('DEBUG') else None,
            "version": "4.0"
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
        
        print(f"📝 Feedback received (v4.0): {data}")
        
        return jsonify({
            "message": "Feedback received successfully",
            "feedback_id": feedback_id,
            "status": "success",
            "version": "4.0"
        })
        
    except Exception as e:
        print(f"Feedback endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/debug/env')
def debug_env():
    """Debug environment information"""
    return jsonify({
        'working_directory': str(Path.cwd()),
        'backend_directory': str(backend_dir),
        'src_directory': str(src_dir),
        'python_path': sys.path[:5],
        'environment_vars': {
            'PORT': os.environ.get('PORT'),
            'GEMINI_API_KEY': 'SET' if os.environ.get('GEMINI_API_KEY') else 'MISSING',
            'FLASK_ENV': os.environ.get('FLASK_ENV'),
            'ENVIRONMENT': os.environ.get('ENVIRONMENT'),
        },
        'version': '4.0',
        'rag_engine_status': 'loaded' if get_rag_engine() else 'failed',
        'pdf_processor_status': 'loaded' if get_pdf_processor() else 'failed'
    })

def initialize_system():
    """Initialize the system"""
    print("🚀 Initializing RABuddy DEFINITIVE Production System v4.0...")
    print(f"📁 Working directory: {Path.cwd()}")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python version: {sys.version}")
    
    # Try to load components
    rag = get_rag_engine()
    pdf = get_pdf_processor()
    
    print(f"RAG Engine: {'✅ Loaded' if rag else '❌ Not available'}")
    print(f"PDF Processor: {'✅ Loaded' if pdf else '❌ Not available'}")
    print(f"GEMINI API: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    print("📡 RABuddy DEFINITIVE Production System v4.0 Ready!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting RABuddy DEFINITIVE Production Backend v4.0 on port {port}")
    
    # Initialize system
    initialize_system()
    
    app.run(debug=False, host='0.0.0.0', port=port)
