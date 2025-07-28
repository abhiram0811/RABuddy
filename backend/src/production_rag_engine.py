#!/usr/bin/env python3
"""
Robust RAG Engine for production deployment
"""

import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import sys

# Handle imports gracefully
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: SentenceTransformers not available")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Google Generative AI not available")

try:
    from pdf_processor import PDFProcessor
    PDF_PROCESSOR_AVAILABLE = True
except ImportError:
    PDF_PROCESSOR_AVAILABLE = False
    print("Warning: PDF Processor not available")

class ProductionRAGEngine:
    """Production-ready RAG engine with graceful degradation"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.pdf_processor = None
        self.gemini_model = None
        self.initialized = False
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize components with error handling"""
        try:
            print("🔧 Initializing RAG components...")
            
            # Initialize embedding model
            if EMBEDDINGS_AVAILABLE:
                try:
                    print("📚 Loading embedding model...")
                    self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
                    print("✅ Embedding model loaded")
                except Exception as e:
                    print(f"❌ Failed to load embedding model: {e}")
            
            # Initialize ChromaDB
            if CHROMADB_AVAILABLE:
                try:
                    print("🗄️ Initializing ChromaDB...")
                    persist_dir = os.path.join(os.getcwd(), 'chroma_store')
                    os.makedirs(persist_dir, exist_ok=True)
                    
                    self.chroma_client = chromadb.PersistentClient(
                        path=persist_dir,
                        settings=Settings(anonymized_telemetry=False)
                    )
                    
                    # Get or create collection
                    collection_name = "rabuddy_documents"
                    try:
                        self.collection = self.chroma_client.get_collection(collection_name)
                        print(f"✅ Loaded existing collection: {collection_name}")
                    except ValueError:
                        self.collection = self.chroma_client.create_collection(
                            name=collection_name,
                            metadata={"description": "RABuddy document chunks"}
                        )
                        print(f"✅ Created new collection: {collection_name}")
                        
                except Exception as e:
                    print(f"❌ Failed to initialize ChromaDB: {e}")
            
            # Initialize Gemini
            if GEMINI_AVAILABLE:
                try:
                    gemini_key = os.getenv('GEMINI_API_KEY')
                    if gemini_key:
                        genai.configure(api_key=gemini_key)
                        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                        print("✅ Gemini client initialized")
                    else:
                        print("⚠️ Gemini API key not found")
                except Exception as e:
                    print(f"❌ Failed to initialize Gemini: {e}")
            
            # Initialize PDF processor
            if PDF_PROCESSOR_AVAILABLE:
                try:
                    self.pdf_processor = PDFProcessor()
                    print("✅ PDF processor initialized")
                except Exception as e:
                    print(f"❌ Failed to initialize PDF processor: {e}")
            
            # Process documents if needed
            if self.collection and self.collection.count() == 0:
                self._process_initial_documents()
            
            self.initialized = True
            print("🎉 RAG engine initialization complete")
            
        except Exception as e:
            print(f"❌ RAG engine initialization failed: {e}")
            self.initialized = False
    
    def _process_initial_documents(self):
        """Process initial PDF documents"""
        try:
            print("📄 Processing initial documents...")
            
            # Look for PDFs in various locations
            pdf_paths = [
                Path("pdfs"),
                Path("../pdfs"),
                Path("./pdfs"),
                Path(os.getcwd()) / "pdfs"
            ]
            
            pdf_files = []
            for pdf_dir in pdf_paths:
                if pdf_dir.exists():
                    pdf_files.extend(list(pdf_dir.glob("*.pdf")))
                    break
            
            if not pdf_files:
                print("⚠️ No PDF files found for processing")
                return
            
            if not self.pdf_processor:
                print("⚠️ PDF processor not available")
                return
            
            for pdf_file in pdf_files[:3]:  # Limit to first 3 PDFs for startup
                try:
                    print(f"📖 Processing: {pdf_file.name}")
                    chunks = self.pdf_processor.process_pdf(str(pdf_file))
                    
                    if chunks:
                        self._add_chunks_to_db(chunks)
                        print(f"✅ Added {len(chunks)} chunks from {pdf_file.name}")
                    
                except Exception as e:
                    print(f"❌ Error processing {pdf_file.name}: {e}")
                    
        except Exception as e:
            print(f"❌ Document processing failed: {e}")
    
    def _add_chunks_to_db(self, chunks: List[Dict[str, Any]]):
        """Add text chunks to the vector database"""
        if not self.collection or not self.embedding_model:
            print("⚠️ Cannot add chunks - collection or embeddings not available")
            return
        
        try:
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [f"chunk_{uuid.uuid4()}" for _ in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
        except Exception as e:
            print(f"❌ Failed to add chunks to database: {e}")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a user query and return an answer"""
        query_id = str(uuid.uuid4())
        
        try:
            if not self.initialized:
                return {
                    "answer": "The RAG system is still initializing. Please try again in a moment.",
                    "sources": [],
                    "session_id": "init-session",
                    "query_id": query_id
                }
            
            # Get relevant documents
            relevant_docs = self._retrieve_documents(question)
            
            # Generate answer
            if self.gemini_model and relevant_docs:
                answer = self._generate_answer_with_context(question, relevant_docs)
            else:
                answer = self._generate_fallback_answer(question)
            
            return {
                "answer": answer,
                "sources": relevant_docs[:3],  # Limit sources
                "session_id": f"rag-{datetime.now().strftime('%Y%m%d')}",
                "query_id": query_id
            }
            
        except Exception as e:
            print(f"❌ Query processing failed: {e}")
            return {
                "answer": f"I encountered an error processing your question: '{question}'. Please try rephrasing or try again later.",
                "sources": [],
                "session_id": "error-session",
                "query_id": query_id
            }
    
    def _retrieve_documents(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the question"""
        try:
            if not self.collection or not self.embedding_model:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([question]).tolist()[0]
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            
            sources = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    sources.append({
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,
                        "source": metadata.get('source', 'Unknown'),
                        "page": metadata.get('page', 'Unknown')
                    })
            
            return sources
            
        except Exception as e:
            print(f"❌ Document retrieval failed: {e}")
            return []
    
    def _generate_answer_with_context(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate answer using Gemini with context"""
        try:
            context = "\n\n".join([doc['content'] for doc in context_docs])
            
            prompt = f"""You are RABuddy, an AI assistant for CSU Housing & Dining Services. 
Answer the following question based on the provided context from official CSU housing documents.

Context:
{context}

Question: {question}

Instructions:
- Provide a helpful, accurate answer based on the context
- If the context doesn't contain relevant information, say so
- Be concise but informative
- Focus on CSU housing policies and procedures

Answer:"""

            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini generation failed: {e}")
            return self._generate_fallback_answer(question)
    
    def _generate_fallback_answer(self, question: str) -> str:
        """Generate a fallback answer when AI generation fails"""
        return f"""I received your question about "{question}". While I'm currently unable to access my full knowledge base, I'm designed to help with CSU Housing & Dining Services information including:

- Housing policies and procedures
- Emergency protocols
- Dining services information
- Residence hall guidelines
- Contact information

Please try asking your question again, or contact CSU Housing & Dining Services directly for immediate assistance."""

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "initialized": self.initialized,
            "components": {
                "embeddings": self.embedding_model is not None,
                "chroma": self.collection is not None,
                "gemini": self.gemini_model is not None,
                "pdf_processor": self.pdf_processor is not None
            },
            "document_count": self.collection.count() if self.collection else 0
        }
