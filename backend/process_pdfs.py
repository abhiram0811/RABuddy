#!/usr/bin/env python3
"""
PDF Processing Script for RABuddy
This script processes PDF documents and populates the ChromaDB vector database
"""

import os
import sys
import shutil
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.rag_engine import RAGEngine
from loguru import logger

def setup_pdf_directory():
    """Ensure PDF directory exists and copy PDFs if needed"""
    pdf_dir = Path("pdfs")
    
    if not pdf_dir.exists():
        pdf_dir.mkdir()
        logger.info("Created pdfs directory")
    
    # Check if PDFs exist in parent directory
    parent_pdf_dir = Path("../pdfs")
    if parent_pdf_dir.exists():
        logger.info("Found PDFs in parent directory, copying...")
        for pdf_file in parent_pdf_dir.glob("*.pdf"):
            dest = pdf_dir / pdf_file.name
            if not dest.exists():
                shutil.copy2(pdf_file, dest)
                logger.info(f"Copied {pdf_file.name}")
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    return pdf_files

def main():
    """Main processing function"""
    logger.info("Starting RABuddy PDF processing...")
    
    # Setup environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv('OPENROUTER_API_KEY'):
        logger.warning("OPENROUTER_API_KEY not set - LLM functionality will be limited")
    
    # Setup PDF directory
    pdf_files = setup_pdf_directory()
    
    if not pdf_files:
        logger.warning("No PDF files found. Please add PDF documents to the 'pdfs' directory.")
        return
    
    # Initialize RAG engine (this will process PDFs automatically)
    try:
        logger.info("Initializing RAG engine...")
        rag_engine = RAGEngine()
        
        # Get status
        status = rag_engine.get_status()
        logger.info(f"RAG engine status: {status}")
        
        # Test with a sample query
        if status.get('status') == 'healthy' and status.get('document_count', 0) > 0:
            logger.info("Testing with sample query...")
            test_result = rag_engine.query("What are the emergency procedures?")
            logger.info(f"Test query successful: {len(test_result['sources'])} sources found")
        
        logger.info("✅ RABuddy setup complete!")
        logger.info(f"📚 Processed {status.get('document_count', 0)} document chunks")
        logger.info("🚀 Ready to start the Flask application")
        
    except Exception as e:
        logger.error(f"Error setting up RAG engine: {str(e)}")
        logger.error("Please check your configuration and try again")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
