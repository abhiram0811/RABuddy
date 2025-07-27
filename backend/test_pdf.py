#!/usr/bin/env python3
"""
Simple PDF processing test for RABuddy
"""

import pdfplumber
from pathlib import Path
import json

def test_pdf_processing():
    """Test PDF processing with the available files"""
    pdf_dir = Path("../pdfs")
    
    if not pdf_dir.exists():
        print("PDF directory not found!")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files:")
    
    results = {}
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                page_count = len(pdf.pages)
                
                # Extract text from first page as sample
                if page_count > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    text_preview = first_page_text[:300] + "..." if first_page_text and len(first_page_text) > 300 else first_page_text
                else:
                    text_preview = "No text extracted"
                
                results[pdf_file.name] = {
                    "pages": page_count,
                    "text_preview": text_preview,
                    "status": "success"
                }
                
                print(f"  - Pages: {page_count}")
                print(f"  - Preview: {text_preview[:100]}...")
                
        except Exception as e:
            results[pdf_file.name] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  - Error: {str(e)}")
    
    # Save results
    with open("pdf_processing_test.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to pdf_processing_test.json")
    return results

if __name__ == "__main__":
    results = test_pdf_processing()
    print("\n" + "="*50)
    print("PDF Processing Test Complete!")
    print("="*50)
