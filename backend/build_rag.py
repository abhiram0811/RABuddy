#!/usr/bin/env python3
"""
Complete RAG Application for RABuddy
This script builds the vector database and tests the full RAG pipeline
"""

import os
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pdfplumber
import tiktoken
import openai
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGEngine:
    """Complete RAG engine for RABuddy"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.openrouter_client = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            logger.info("🚀 Initializing RAG Engine...")
            
            # Initialize embedding model
            logger.info("📚 Loading embedding model...")
            self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
            logger.info("✅ Embedding model loaded")
            
            # Initialize ChromaDB
            logger.info("🗃️ Initializing ChromaDB...")
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
                logger.info(f"📂 Loaded existing collection: {collection_name}")
            except (ValueError, chromadb.errors.NotFoundError):
                logger.info(f"📝 Creating new collection: {collection_name}")
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "RABuddy document chunks"}
                )
                logger.info(f"📂 Created new collection: {collection_name}")
            
            # Initialize OpenRouter client
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if openrouter_key:
                self.openrouter_client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key
                )
                logger.info("🤖 OpenRouter client initialized")
            else:
                logger.warning("⚠️ OpenRouter API key not found")
            
            # Check if we need to process documents
            doc_count = self.collection.count()
            if doc_count == 0:
                logger.info("📄 No documents found, processing PDFs...")
                self._process_documents()
            else:
                logger.info(f"📚 Found {doc_count} existing document chunks")
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG engine: {str(e)}")
            raise
    
    def _process_documents(self):
        """Process PDF documents and add to vector database"""
        logger.info("📄 Processing PDF documents...")
        
        pdf_dir = Path("../pdfs")
        if not pdf_dir.exists():
            logger.warning(f"📁 PDF directory not found: {pdf_dir}")
            return
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("📄 No PDF files found to process")
            return
        
        total_chunks = 0
        for pdf_file in pdf_files:
            try:
                logger.info(f"📖 Processing: {pdf_file.name}")
                chunks = self._extract_pdf_chunks(str(pdf_file))
                
                if chunks:
                    self._add_chunks_to_db(chunks, pdf_file.name)
                    total_chunks += len(chunks)
                    logger.info(f"✅ Added {len(chunks)} chunks from {pdf_file.name}")
                else:
                    logger.warning(f"⚠️ No chunks extracted from {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {pdf_file.name}: {str(e)}")
        
        logger.info(f"🎉 Total chunks processed: {total_chunks}")
    
    def _extract_pdf_chunks(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text chunks from PDF"""
        chunks = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        # Clean the text
                        clean_text = self._clean_text(text)
                        
                        # Split into chunks
                        text_chunks = self._split_text_by_tokens(clean_text, chunk_size=400, overlap=50)
                        
                        for chunk_idx, chunk_text in enumerate(text_chunks):
                            if chunk_text.strip():
                                chunks.append({
                                    'text': chunk_text.strip(),
                                    'filename': Path(pdf_path).name,
                                    'page_number': page_num,
                                    'chunk_index': chunk_idx,
                                    'token_count': len(self.tokenizer.encode(chunk_text))
                                })
        
        except Exception as e:
            logger.error(f"❌ Error extracting chunks from {pdf_path}: {str(e)}")
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers patterns
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text)
        
        # Fix common OCR issues
        text = text.replace('—', '-')
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _split_text_by_tokens(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split text into chunks based on token count"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            if end == len(tokens):
                break
            start = end - overlap
        
        return chunks
    
    def _add_chunks_to_db(self, chunks: List[Dict[str, Any]], filename: str):
        """Add document chunks to ChromaDB"""
        if not chunks:
            return
        
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
        logger.info(f"🔗 Generating embeddings for {len(documents)} chunks...")
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Process a user query and return an answer with sources"""
        query_id = str(uuid.uuid4())
        
        try:
            logger.info(f"🔍 Processing query: {question}")
            
            # Retrieve relevant documents
            query_embedding = self.embedding_model.encode([question]).tolist()[0]
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Prepare context
            context_chunks = []
            sources = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                context_chunks.append(f"[Source {i+1}] {doc}")
                sources.append({
                    'filename': metadata['filename'],
                    'page_number': metadata['page_number'],
                    'relevance_score': round(1 - distance, 3),
                    'text_preview': doc[:200] + "..." if len(doc) > 200 else doc
                })
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context_chunks)
            
            logger.info(f"✅ Query processed successfully")
            
            return {
                'query_id': query_id,
                'answer': answer,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing query {query_id}: {str(e)}")
            return {
                'query_id': query_id,
                'answer': "I'm sorry, I encountered an error while processing your question. Please try again.",
                'sources': []
            }
    
    def _generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate an answer using the LLM"""
        if not self.openrouter_client:
            return "I found relevant information but the AI response system is not available. Please check the configuration."
        
        context = "\n\n".join(context_chunks)
        
        prompt = f"""You are RABuddy, an AI assistant helping Resident Assistants (RAs) at Colorado State University Housing & Dining Services. 

Based on the following context from official Housing & Dining documents, answer the user's question accurately and helpfully.

Context:
{context}

Question: {question}

Instructions:
- Provide a clear, accurate answer based on the context
- Reference specific policies, procedures, or contacts when relevant
- If the context doesn't contain enough information, say so clearly
- Keep your response helpful and professional
- Focus on actionable information for RAs
- Be concise but thorough

Answer:"""

        try:
            response = self.openrouter_client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {str(e)}")
            return "I found relevant information in the documents, but I'm having trouble generating a response right now. Please try again later."
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        try:
            doc_count = self.collection.count() if self.collection else 0
            
            return {
                'status': 'healthy',
                'document_count': doc_count,
                'embedding_model': 'BAAI/bge-small-en-v1.5',
                'llm_model': 'deepseek/deepseek-chat',
                'vector_db': 'ChromaDB',
                'openrouter_configured': bool(os.getenv('OPENROUTER_API_KEY'))
            }
        except Exception as e:
            logger.error(f"❌ Error getting status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    """Main function to build and test the RAG system"""
    logger.info("🎯 Starting RABuddy RAG System Build...")
    
    # Initialize RAG engine
    rag_engine = RAGEngine()
    
    # Get status
    status = rag_engine.get_status()
    logger.info(f"📊 System Status: {json.dumps(status, indent=2)}")
    
    # Test with sample queries
    test_queries = [
        "What should I do for lockouts after midnight?",
        "Who should I contact for facilities emergencies?",
        "What items are prohibited in residence halls?",
        "What's the protocol for bias-related incidents?"
    ]
    
    logger.info("🧪 Testing with sample queries...")
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"📝 Test Query {i}: {query}")
        result = rag_engine.query(query)
        
        print(f"\n{'='*60}")
        print(f"QUERY {i}: {query}")
        print(f"{'='*60}")
        print(f"ANSWER: {result['answer']}")
        print(f"\nSOURCES ({len(result['sources'])}):")
        for j, source in enumerate(result['sources'], 1):
            print(f"  {j}. {source['filename']} (Page {source['page_number']}) - Score: {source['relevance_score']}")
            print(f"     Preview: {source['text_preview'][:100]}...")
        print()
    
    logger.info("🎉 RAG System Build and Test Complete!")
    return rag_engine

if __name__ == "__main__":
    rag_engine = main()
