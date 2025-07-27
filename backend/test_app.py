#!/usr/bin/env python3
"""
Simple test Flask app to verify the setup works
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "RABuddy Backend"})

@app.route('/api/test')
def test_endpoint():
    try:
        # Check for PDF files
        backend_path = Path(__file__).parent
        pdfs_path = backend_path.parent / "pdfs"
        
        pdf_count = 0
        pdf_files = []
        
        if pdfs_path.exists():
            pdf_files = list(pdfs_path.glob("*.pdf"))
            pdf_count = len(pdf_files)
        
        return jsonify({
            "message": "RABuddy backend is working!",
            "pdf_files_found": pdf_count,
            "pdf_files": [f.name for f in pdf_files],
            "pdfs_directory": str(pdfs_path),
            "directory_exists": pdfs_path.exists()
        })
    except Exception as e:
        return jsonify({
            "message": "RABuddy backend has an error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting RABuddy test server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
