import re
import pdfplumber
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger
import tiktoken

class PDFProcessor:
    """Process PDF documents and extract text chunks with metadata"""
    
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a PDF file and return chunks with metadata"""
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Extract text using pdfplumber
            page_texts = self._extract_with_plumber(pdf_path)
            
            if not page_texts:
                logger.warning(f"No text extracted from {pdf_path}")
                return []
            
            # Create chunks
            chunks = self._create_chunks(page_texts, Path(pdf_path).name)
            
            logger.info(f"Created {len(chunks)} chunks from {pdf_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
    
    
    def _extract_with_plumber(self, pdf_path: str) -> Dict[int, str]:
        """Extract text using pdfplumber"""
        page_texts = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        page_texts[i + 1] = self._clean_text(text)
        
        except Exception as e:
            logger.error(f"Error with pdfplumber extraction: {str(e)}")
        
        return page_texts
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers patterns
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text)  # Remove trailing page numbers
        
        # Fix common OCR issues
        text = text.replace('—', '-')
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove multiple consecutive periods
        text = re.sub(r'\.{3,}', '...', text)
        
        return text.strip()
    
    def _create_chunks(self, page_texts: Dict[int, str], filename: str) -> List[Dict[str, Any]]:
        """Create chunks from page texts"""
        chunks = []
        
        for page_num, text in page_texts.items():
            if not text.strip():
                continue
            
            # Split text into chunks based on token count
            page_chunks = self._split_text_by_tokens(text)
            
            for i, chunk_text in enumerate(page_chunks):
                if chunk_text.strip():
                    chunks.append({
                        'text': chunk_text.strip(),
                        'filename': filename,
                        'page_number': page_num,
                        'chunk_index': i,
                        'token_count': len(self.tokenizer.encode(chunk_text))
                    })
        
        return chunks
    
    def _split_text_by_tokens(self, text: str) -> List[str]:
        """Split text into chunks based on token count"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            # Calculate end position with overlap
            end = min(start + self.chunk_size, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Break if we're at the end
            if end == len(tokens):
                break
        
        return chunks
    
    def get_text_preview(self, pdf_path: str, max_chars: int = 500) -> str:
        """Get a preview of the PDF content"""
        try:
            page_texts = self._extract_with_plumber(pdf_path)
            
            if page_texts:
                # Get text from first page
                first_page = min(page_texts.keys())
                text = page_texts[first_page]
                
                if len(text) > max_chars:
                    return text[:max_chars] + "..."
                return text
            
            return "No text could be extracted from this PDF."
            
        except Exception as e:
            logger.error(f"Error getting preview for {pdf_path}: {str(e)}")
            return f"Error reading PDF: {str(e)}"
