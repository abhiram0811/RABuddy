#!/usr/bin/env python3
"""
DIRECT RAG APP ENTRY POINT - NO FALLBACKS!
"""

# Direct import - no fallbacks!
from guaranteed_rag_app import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀🔥 DIRECT RAG APP START on port {port} 🔥🚀")
    app.run(host='0.0.0.0', port=port, debug=False)
