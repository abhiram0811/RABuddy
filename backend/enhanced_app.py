#!/usr/bin/env python3
"""
RABuddy Enhanced Backend with PDF Re-embedding
Features: Better chunking, inline citations, CSU-themed responses
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
import logging
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, 
     origins=["*"], 
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Accept", "ngrok-skip-browser-warning", "Authorization"],
     expose_headers=["Content-Type"],
     supports_credentials=False)

# Global RAG components
chroma_client = None
chroma_collection = None
gemini_model = None
embedding_model = None

def setup_enhanced_embedding():
    """Setup sentence transformers for better embeddings"""
    global embedding_model
    try:
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✅ Enhanced embedding model loaded")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load embedding model: {e}")
        return False

def process_pdfs_enhanced():
    """Process PDFs with better chunking and metadata"""
    try:
        from PyPDF2 import PdfReader
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings
        
        # Initialize components
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Use existing ChromaDB path or create new one
        chroma_store_path = Path(__file__).parent / "chroma_store_enhanced"
        
        # Create new ChromaDB client
        chroma_client = chromadb.PersistentClient(
            path=str(chroma_store_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Try to get existing collection or create new one
        collection_name = "csu_housing_docs_enhanced"
        try:
            # Try to delete existing collection if it exists
            chroma_client.delete_collection(collection_name)
            logger.info(f"🗑️ Removed existing collection: {collection_name}")
        except:
            logger.info(f"📝 Creating new collection: {collection_name}")
        
        # Create collection with metadata
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "CSU Housing & Dining Documents with Enhanced Chunking"}
        )
        
        # Process PDFs from the pdfs directory
        pdfs_dir = Path(__file__).parent.parent / "pdfs"
        documents = []
        metadatas = []
        ids = []
        
        for pdf_path in pdfs_dir.glob("*.pdf"):
            logger.info(f"📄 Processing: {pdf_path.name}")
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PdfReader(file)  # Updated to use PdfReader
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        
                        if text.strip():
                            # Better chunking: split by sentences and group
                            sentences = text.replace('\n', ' ').split('. ')
                            
                            # Create chunks of 3-4 sentences for better context
                            chunk_size = 3
                            for i in range(0, len(sentences), chunk_size):
                                chunk_sentences = sentences[i:i + chunk_size]
                                chunk_text = '. '.join(chunk_sentences).strip()
                                
                                if len(chunk_text) > 50:  # Skip very short chunks
                                    doc_id = f"{pdf_path.stem}_page_{page_num + 1}_chunk_{i // chunk_size + 1}"
                                    
                                    documents.append(chunk_text)
                                    metadatas.append({
                                        "source": pdf_path.name,
                                        "page": page_num + 1,
                                        "chunk_id": i // chunk_size + 1,
                                        "doc_type": "csu_housing_policy",
                                        "total_pages": len(pdf_reader.pages)
                                    })
                                    ids.append(doc_id)
            
            except Exception as e:
                logger.error(f"❌ Failed to process {pdf_path.name}: {e}")
                continue
        
        # Add documents to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
        
        logger.info(f"✅ Successfully processed {len(documents)} document chunks")
        logger.info(f"📚 Documents from {len(list(pdfs_dir.glob('*.pdf')))} PDF files")
        
        return True, len(documents)
        
    except Exception as e:
        logger.error(f"💥 PDF processing failed: {e}")
        return False, 0

def initialize_enhanced_rag():
    """Initialize enhanced RAG system"""
    global chroma_client, chroma_collection, gemini_model
    
    try:
        logger.info("🚀 Initializing Enhanced RAG system...")
        
        # 1. Setup embeddings
        if not setup_enhanced_embedding():
            return False
        
        # 2. Process PDFs with enhanced chunking
        success, doc_count = process_pdfs_enhanced()
        if not success:
            return False
        
        # 3. Initialize ChromaDB connection
        try:
            import chromadb
            from chromadb.config import Settings
            
            chroma_store_path = Path(__file__).parent / "chroma_store_enhanced"
            chroma_client = chromadb.PersistentClient(
                path=str(chroma_store_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            chroma_collection = chroma_client.get_collection("csu_housing_docs_enhanced")
            actual_count = chroma_collection.count()
            logger.info(f"✅ Connected to ChromaDB: {actual_count} enhanced document chunks")
            
        except Exception as e:
            logger.error(f"❌ ChromaDB connection failed: {e}")
            return False
        
        # 4. Initialize Gemini
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("❌ GEMINI_API_KEY not found")
                return False
            
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test connection
            test_response = gemini_model.generate_content("Hello")
            logger.info("✅ Gemini model initialized and tested")
            
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            return False
        
        logger.info("🎉 Enhanced RAG system initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Enhanced RAG initialization failed: {e}")
        return False

def query_enhanced_rag(question: str) -> dict:
    """Enhanced RAG query with better context and inline citations"""
    try:
        session_id = str(uuid.uuid4())
        
        if not chroma_collection or not gemini_model or not embedding_model:
            return {
                "answer": "Enhanced RAG system not properly initialized.",
                "sources": [],
                "session_id": session_id,
                "method": "error"
            }
        
        # Query ChromaDB with enhanced search
        try:
            search_results = chroma_collection.query(
                query_texts=[question],
                n_results=8,  # Get more results for better context
                include=['documents', 'metadatas', 'distances']
            )
            
            relevant_docs = []
            if search_results['documents'] and search_results['documents'][0]:
                for i, doc in enumerate(search_results['documents'][0]):
                    metadata = search_results['metadatas'][0][i] if search_results['metadatas'][0] else {}
                    distance = search_results['distances'][0][i] if search_results['distances'][0] else 1.0
                    
                    # Only include highly relevant documents
                    if distance < 0.7:  # Stricter relevance threshold
                        relevant_docs.append({
                            "content": doc,
                            "metadata": metadata,
                            "relevance_score": round(1 - distance, 3),
                            "source_number": len(relevant_docs) + 1
                        })
            
            logger.info(f"Found {len(relevant_docs)} highly relevant documents")
            
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            relevant_docs = []
        
        # Generate enhanced response with inline citations
        try:
            source_map = {}  # Initialize source_map early to avoid NameError
            
            if relevant_docs:
                # Create context with source numbers
                context_parts = []
                
                for doc in relevant_docs[:6]:  # Use top 6 documents
                    source_num = doc["source_number"]
                    source_info = f"{doc['metadata'].get('source', 'Unknown')} (Page {doc['metadata'].get('page', 'Unknown')})"
                    source_map[source_num] = source_info
                    
                    context_parts.append(f"[Source {source_num}] {doc['content']}")
                
                context = "\n\n".join(context_parts)
                
                prompt = f"""You are RABuddy, the official AI assistant for Colorado State University Housing & Dining Services.

You help Resident Assistants (RAs) and housing staff with policy questions, procedures, and resident support.

INSTRUCTIONS:
1. Answer based ONLY on the provided context from official CSU Housing documents
2. Include inline citations in your response using (Source X) format
3. Be specific and cite the exact source for each piece of information
4. If information isn't in the context, clearly state that
5. Use a professional but friendly tone appropriate for CSU staff

CONTEXT FROM CSU HOUSING DOCUMENTS:
{context}

QUESTION: {question}

RESPONSE GUIDELINES:
- Start with a direct answer
- Include specific details from the documents
- Use inline citations: (Source 1), (Source 2), etc.
- End with a helpful summary if appropriate
- If the context doesn't fully answer the question, acknowledge this and suggest contacting Housing & Dining Services

Please provide a comprehensive answer with proper citations:"""
            else:
                prompt = f"""You are RABuddy, the AI assistant for CSU Housing & Dining Services.

QUESTION: {question}

I don't have specific information about this topic in my current document database. 

For accurate and up-to-date information about CSU Housing & Dining policies and procedures, I recommend:

1. Contacting Housing & Dining Services directly at (970) 491-5136
2. Visiting the CSU Housing website: housing.colostate.edu
3. Checking with your Area Coordinator or Housing professional staff
4. Reviewing the most current housing contract and policies

Is there a different housing-related question I can help you with?"""
            
            response = gemini_model.generate_content(prompt)
            
            # Prepare sources for frontend
            formatted_sources = []
            for doc in relevant_docs[:5]:
                formatted_sources.append({
                    "source_number": doc["source_number"],
                    "filename": doc["metadata"].get("source", "Unknown Document"),
                    "page_number": doc["metadata"].get("page", 0),
                    "relevance_score": doc["relevance_score"],
                    "text_preview": doc["content"][:200] + "...",
                    "metadata": doc["metadata"]
                })
            
            return {
                "answer": response.text,
                "sources": formatted_sources,
                "session_id": session_id,
                "method": "enhanced_rag_gemini",
                "document_count": len(relevant_docs),
                "processing_info": {
                    "total_chunks_searched": len(search_results['documents'][0]) if search_results['documents'] else 0,
                    "relevant_chunks_used": len(relevant_docs),
                    "citation_sources": len(source_map)
                }
            }
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            
            return {
                "answer": "I'm sorry, I encountered an issue generating a response. Please try rephrasing your question or contact CSU Housing & Dining Services directly at (970) 491-5136.",
                "sources": [{"source_number": i+1, "filename": doc["metadata"].get("source", "Unknown"), "text_preview": doc["content"][:200] + "..."} for i, doc in enumerate(relevant_docs[:3])],
                "session_id": session_id,
                "method": "fallback",
                "error": str(e)
            }
            
    except Exception as e:
        logger.error(f"Enhanced query processing failed: {e}")
        return {
            "answer": "I'm sorry, I encountered an error processing your question. Please try again or contact CSU Housing & Dining Services.",
            "sources": [],
            "session_id": str(uuid.uuid4()),
            "method": "error",
            "error": str(e)
        }

# Routes
@app.route('/')
def health_check():
    """Enhanced health check"""
    doc_count = 0
    collection_name = "unknown"
    
    if chroma_collection:
        try:
            doc_count = chroma_collection.count()
            collection_name = chroma_collection.name
        except:
            pass
    
    return jsonify({
        "service": "RABuddy Enhanced Backend",
        "version": "2.0.0",
        "status": "healthy",
        "deployment": "ngrok",
        "timestamp": datetime.now().isoformat(),
        "rag_status": {
            "chromadb": chroma_collection is not None,
            "gemini": gemini_model is not None,
            "embeddings": embedding_model is not None,
            "documents": doc_count,
            "collection": collection_name
        },
        "features": [
            "Enhanced PDF chunking",
            "Inline citations",
            "CSU-specific responses",
            "Better relevance filtering"
        ]
    })

@app.route('/api/query', methods=['POST', 'OPTIONS'])
def api_query():
    """Enhanced RAG query endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight OK'})
    
    try:
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        logger.info(f"Processing enhanced query: {question[:100]}...")
        result = query_enhanced_rag(question)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API query failed: {e}")
        return jsonify({
            "error": "Failed to process query",
            "message": str(e),
            "session_id": str(uuid.uuid4())
        }), 500

@app.route('/api/health')
def api_health():
    """Enhanced health endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "enhanced_v2.0",
        "components": {
            "chromadb": chroma_collection is not None,
            "gemini": gemini_model is not None,
            "embeddings": embedding_model is not None,
            "environment": {
                "gemini_api_key": bool(os.getenv('GEMINI_API_KEY'))
            }
        }
    })

@app.route('/api/debug')
def api_debug():
    """Enhanced debug endpoint"""
    if not chroma_collection:
        return jsonify({"error": "ChromaDB not initialized"}), 500
    
    try:
        # Get sample documents with metadata
        sample_results = chroma_collection.query(
            query_texts=["housing policy"],
            n_results=5,
            include=['documents', 'metadatas']
        )
        
        return jsonify({
            "collection_name": chroma_collection.name,
            "document_count": chroma_collection.count(),
            "sample_documents": [
                {
                    "content": doc[:150] + "...",
                    "metadata": sample_results['metadatas'][0][i] if sample_results['metadatas'][0] else {},
                    "source": sample_results['metadatas'][0][i].get('source', 'Unknown') if sample_results['metadatas'][0] else 'Unknown'
                }
                for i, doc in enumerate(sample_results['documents'][0])
            ] if sample_results['documents'] else [],
            "version": "enhanced_v2.0"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rebuild', methods=['POST'])
def rebuild_database():
    """Rebuild the vector database"""
    try:
        logger.info("🔄 Rebuilding vector database...")
        success = initialize_enhanced_rag()
        
        if success:
            return jsonify({
                "message": "Vector database rebuilt successfully",
                "document_count": chroma_collection.count() if chroma_collection else 0,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to rebuild database"}), 500
            
    except Exception as e:
        logger.error(f"Database rebuild failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize enhanced RAG system
    rag_ready = initialize_enhanced_rag()
    
    if not rag_ready:
        logger.error("❌ Enhanced RAG system failed to initialize")
        exit(1)
    
    # Start Flask server
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"🚀 RABuddy Enhanced Backend starting on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
