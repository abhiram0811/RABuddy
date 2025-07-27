import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger
import google.generativeai as genai

from pdf_processor import PDFProcessor

class RAGEngine:
    """Main RAG engine for processing queries and retrieving relevant information"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.pdf_processor = PDFProcessor()
        self.gemini_model = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
            
            # Initialize ChromaDB
            logger.info("Initializing ChromaDB...")
            persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_store')
            os.makedirs(persist_dir, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            collection_name = "rabuddy_documents"
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"Loaded existing collection: {collection_name}")
            except ValueError:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "RABuddy document chunks"}
                )
                logger.info(f"Created new collection: {collection_name}")
            
            # Initialize Gemini client
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini client initialized")
            else:
                logger.warning("Gemini API key not found")
            
            # Process PDFs if collection is empty
            if self.collection.count() == 0:
                self._process_documents()
            
        except Exception as e:
            logger.error(f"Error initializing RAG engine: {str(e)}")
            raise
    
    def _process_documents(self):
        """Process PDF documents and add to vector database"""
        logger.info("Processing PDF documents...")
        
        pdf_dir = Path("../pdfs")
        if not pdf_dir.exists():
            logger.warning(f"PDF directory not found: {pdf_dir}")
            return
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("No PDF files found to process")
            return
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing: {pdf_file.name}")
                chunks = self.pdf_processor.process_pdf(str(pdf_file))
                
                if chunks:
                    self._add_chunks_to_db(chunks)
                    logger.info(f"Added {len(chunks)} chunks from {pdf_file.name}")
                else:
                    logger.warning(f"No chunks extracted from {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
    
    def _add_chunks_to_db(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to ChromaDB"""
        if not chunks:
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            documents.append(chunk['text'])
            metadatas.append({
                'filename': chunk['filename'],
                'page_number': chunk['page_number'],
                'chunk_index': chunk['chunk_index'],
                'source_type': 'pdf'
            })
            ids.append(f"{chunk['filename']}_page_{chunk['page_number']}_chunk_{chunk['chunk_index']}")
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
    
    def _enhance_query(self, question: str) -> str:
        """Enhance query with related terms for better retrieval"""
        # Common synonyms and related terms for housing topics
        enhancements = {
            'wallpaper': 'wallpaper decorating walls decoration removable adhesive',
            'lockout': 'lockout locked out key access door entry',
            'guest': 'guest visitor overnight staying policy',
            'emergency': 'emergency urgent crisis safety evacuation',
            'prohibited': 'prohibited banned forbidden not allowed restricted',
            'contact': 'contact phone number call reach emergency',
            'policy': 'policy rule regulation guideline procedure',
            'room': 'room residence hall dorm dormitory space',
            'decorating': 'decorating decoration decor walls hanging items',
            'cooking': 'cooking kitchen appliance food preparation',
            'cleaning': 'cleaning maintenance housekeeping supplies'
        }
        
        enhanced = question.lower()
        for key, terms in enhancements.items():
            if key in enhanced:
                enhanced = f"{enhanced} {terms}"
                break
        
        return enhanced
    
    def query(self, question: str, top_k: int = 8) -> Dict[str, Any]:
        """Process a user query and return an answer with sources"""
        query_id = str(uuid.uuid4())
        
        try:
            # Enhance query with related terms for better retrieval
            enhanced_question = self._enhance_query(question)
            logger.info(f"Original: {question}")
            logger.info(f"Enhanced: {enhanced_question}")
            
            # Retrieve relevant documents
            logger.info(f"Retrieving documents for query: {enhanced_question}")
            
            query_embedding = self.embedding_model.encode([enhanced_question]).tolist()[0]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Filter results by relevance threshold (distance < 0.8 means similarity > 0.2)
            filtered_results = {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
            relevance_threshold = 0.8  # Lowered from 0.7 to be less strict
            
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            ):
                if distance < relevance_threshold:  # Keep only relevant chunks
                    filtered_results['documents'][0].append(doc)
                    filtered_results['metadatas'][0].append(metadata)
                    filtered_results['distances'][0].append(distance)
            
            # Use filtered results, but fall back to top 3 unfiltered if nothing passes threshold
            if not filtered_results['documents'][0] and results['documents'][0]:
                logger.info(f"No results passed threshold {relevance_threshold}, using top 3 unfiltered results")
                # Use top 3 results even if they don't pass strict threshold
                for i in range(min(3, len(results['documents'][0]))):
                    filtered_results['documents'][0].append(results['documents'][0][i])
                    filtered_results['metadatas'][0].append(results['metadatas'][0][i])
                    filtered_results['distances'][0].append(results['distances'][0][i])
            
            results = filtered_results
            
            if not results['documents'][0]:
                return {
                    'query_id': query_id,
                    'answer': "I couldn't find relevant information in the provided documents to answer your question. Please try rephrasing or contact Housing & Dining Services directly.",
                    'sources': []
                }
            
            # Prepare context with source numbering
            context_chunks = []
            sources = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                # Add cleaner source reference
                context_chunks.append(f"[Source {i+1}] From {metadata['filename']}, Page {metadata['page_number']}:\n{doc}")
                sources.append({
                    'source_number': i+1,
                    'filename': metadata['filename'],
                    'page_number': metadata['page_number'],
                    'relevance_score': round(1 - distance, 3),
                    'text_preview': doc[:150] + "..." if len(doc) > 150 else doc
                })
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context_chunks)
            
            # Log the query
            self._log_query(query_id, question, answer, sources)
            
            return {
                'query_id': query_id,
                'answer': answer,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error processing query {query_id}: {str(e)}")
            return {
                'query_id': query_id,
                'answer': "I'm sorry, I encountered an error while processing your question. Please try again.",
                'sources': []
            }
    
    def _generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate an answer using the LLM"""
        if not self.gemini_model:
            return "LLM service is not available. Please check the configuration."
        
        context = "\n\n".join(context_chunks)
        
        prompt = f"""You are RABuddy, an AI assistant for CSU Resident Assistants. Answer questions using ONLY the provided context.

Context from official CSU Housing documents:
{context}

Question: {question}

CRITICAL INSTRUCTIONS:
- Answer ONLY based on the provided context - do not add external knowledge
- Be concise and direct (2-4 sentences max unless complex procedure)
- Use inline citations: (Source 1), (Source 2), etc. after each fact
- If the context contains partial or indirect information, use it to provide the best answer possible
- Look for synonyms and related terms (e.g., "wallpaper" might be in "decorating items")
- If information is completely missing from context, state: "This information is not available in the provided documents"
- For procedures, use numbered steps with citations
- Never guess or make assumptions beyond what's in the context
- Quote exact phrases from documents when possible

Format: Brief answer with (Source X) citations inline.

Answer:"""

        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=300,
                    top_p=0.9
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again later."
    
    def _log_query(self, query_id: str, question: str, answer: str, sources: List[Dict]):
        """Log query details for analytics"""
        log_data = {
            'query_id': query_id,
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'num_sources': len(sources),
            'source_files': list(set(s['filename'] for s in sources))
        }
        
        logger.info(f"Query logged: {json.dumps(log_data)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        try:
            doc_count = self.collection.count() if self.collection else 0
            
            return {
                'status': 'healthy',
                'document_count': doc_count,
                'embedding_model': 'BAAI/bge-small-en-v1.5',
                'llm_model': 'gemini-1.5-flash',
                'vector_db': 'ChromaDB'
            }
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
