#!/usr/bin/env python3
"""
NUCLEAR WSGI - This WILL work!
"""
import os

print("�🚀🚀 NUCLEAR WSGI STARTING!")

# Import the nuclear app - zero dependencies
from nuclear_app import app

print("✅ NUCLEAR APP IMPORTED SUCCESSFULLY!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 NUCLEAR: Starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
