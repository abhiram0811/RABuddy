#!/usr/bin/env python3
"""
EMERGENCY RAG APP - FORCES INSTALLATION AND RUNNING
This will install dependencies at runtime and start the RAG app
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required packages at runtime"""
    print("🔧 Installing RAG dependencies at runtime...")
    
    packages = [
        'chromadb',
        'sentence-transformers', 
        'google-generativeai',
        'numpy',
        'requests'
    ]
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
            print(f"✅ {package} installed successfully")
        except Exception as e:
            print(f"⚠️ Failed to install {package}: {e}")

def main():
    print("🚀🔥 EMERGENCY RAG APP STARTING 🔥🚀")
    
    # Install dependencies first
    install_dependencies()
    
    # Now import and run the RAG app
    try:
        from guaranteed_rag_app import app
        print("✅ Successfully imported guaranteed_rag_app after dependency installation")
        
        port = int(os.environ.get('PORT', 10000))
        print(f"🚀 Starting RAG app on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Failed to start RAG app: {e}")
        
        # Create emergency Flask app
        from flask import Flask, jsonify
        emergency_app = Flask(__name__)
        
        @emergency_app.route('/')
        def home():
            return jsonify({
                "service": "RABuddy Emergency Mode",
                "status": "EMERGENCY_DEPLOYMENT",
                "message": "Dependencies installing at runtime",
                "error": str(e)
            })
        
        port = int(os.environ.get('PORT', 10000))
        print(f"🚨 Starting emergency app on port {port}")
        emergency_app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
