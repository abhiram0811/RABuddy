# RABuddy - Clean Architecture

## 🎯 Project Structure
```
RABuddy/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── chroma_store/       # Your existing ChromaDB
│   └── .env               # API keys
├── frontend/              # Your Next.js frontend
├── pdfs/                  # Housing documents
├── ngrok.yml             # ngrok configuration
├── start_backend.sh      # Backend startup script
└── start_ngrok.sh        # ngrok tunnel script
```

## 🚀 Quick Start

### 1. Start Backend
```bash
./start_backend.sh
```

### 2. Start ngrok (separate terminal)
```bash
./start_ngrok.sh
```

### 3. Update Frontend
Use the ngrok URL in your Vercel frontend:
```
https://your-backend-url.ngrok.io
```

## 🔌 API Endpoints

- `GET /` - Health check with ChromaDB status
- `POST /api/query` - RAG queries using your indexed PDFs
- `GET /api/health` - Detailed component status
- `GET /api/debug` - ChromaDB contents inspection

## 🏗️ Architecture

**ChromaDB** (Your existing data) → **Gemini** (Generation) → **ngrok** (Public access)

The backend uses your existing ChromaDB store with all your indexed housing documents and connects to Gemini for response generation.
