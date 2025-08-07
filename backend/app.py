#!/usr/bin/env python3
"""
RABuddy Backend Entry Point - Enhanced with better PDF processing
"""

from enhanced_app import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 RABuddy Enhanced Backend starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
