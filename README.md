# RABuddy - AI Assistant for CSU Housing & Dining

RABuddy is an AI-powered assistant designed to help Resident Assistants (RAs) at Colorado State University Housing & Dining Services quickly find information about policies, procedures, emergency contacts, and more.

## 🏗️ Architecture

- **Backend**: Flask API with ChromaDB vector database
- **Frontend**: Next.js with Tailwind CSS
- **LLM**: OpenRouter API with DeepSeek Chat model
- **Embeddings**: BAAI/bge-small-en-v1.5
- **Logging**: Loguru + optional Supabase
- **Hosting**: Render (backend) + Vercel (frontend)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenRouter API key
- (Optional) Supabase account

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
SUPABASE_URL=your_supabase_url_here  # Optional
SUPABASE_KEY=your_supabase_key_here  # Optional
```

5. Copy your PDF documents to the `pdfs/` directory

6. Run the application:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
RABuddy/
├── backend/
│   ├── src/
│   │   ├── app.py              # Flask app factory
│   │   ├── routes.py           # API endpoints
│   │   ├── rag_engine.py       # Main RAG logic
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   └── feedback_logger.py  # Feedback logging
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   └── components/
│   │       ├── ChatInterface.tsx
│   │       └── Header.tsx
│   ├── package.json
│   └── next.config.js
└── pdfs/                       # Place your PDF documents here
```

## 🔌 API Endpoints

### POST /api/query
Query the RAG system with a question.

**Request:**
```json
{
  "question": "What's the protocol for lockouts after midnight?"
}
```

**Response:**
```json
{
  "answer": "According to the duty protocol...",
  "sources": [
    {
      "filename": "duty-manual.pdf",
      "page_number": 15,
      "relevance_score": 0.89,
      "text_preview": "Lockout procedures after midnight..."
    }
  ],
  "query_id": "uuid-string"
}
```

### POST /api/feedback
Log user feedback for an answer.

**Request:**
```json
{
  "query_id": "uuid-string",
  "feedback_type": "positive",
  "comment": "Very helpful!"
}
```

### GET /api/status
Get system status and statistics.

## 🚀 Deployment

### Backend (Render)

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy using the included Dockerfile

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set the root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com/api`
4. Deploy

## 📊 Features

- **Intelligent Document Retrieval**: Uses semantic search to find relevant information
- **Source Attribution**: Shows exact page numbers and document sources
- **User Feedback**: Thumbs up/down with optional comments
- **Real-time Chat Interface**: Clean, responsive UI for easy interaction
- **Comprehensive Logging**: Track usage patterns and feedback
- **Free Hosting**: Designed to run on free tiers of Render and Vercel

## 🔧 Configuration

### Embedding Model
The system uses `BAAI/bge-small-en-v1.5` for document embeddings. You can change this in `rag_engine.py`:

```python
self.embedding_model = SentenceTransformer('your-preferred-model')
```

### LLM Model
Uses OpenRouter's DeepSeek Chat model. Change in `rag_engine.py`:

```python
response = self.openrouter_client.chat.completions.create(
    model="your-preferred-model",
    # ...
)
```

### Chunk Size
Adjust document chunking in `pdf_processor.py`:

```python
def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
```

## 🐛 Troubleshooting

### PDF Processing Issues
- Ensure PDFs are readable (not corrupted)
- For scanned PDFs, consider using OCR preprocessing
- Check logs for specific extraction errors

### ChromaDB Persistence
- Ensure the `chroma_store` directory has write permissions
- On Render, use a persistent disk or volume

### API Rate Limits
- OpenRouter has rate limits; implement retry logic if needed
- Monitor usage in OpenRouter dashboard

## 📝 License

This project is intended for educational and internal use at Colorado State University Housing & Dining Services.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For technical support or questions about deployment, contact the development team.

---

Built with ❤️ for Colorado State University Housing & Dining Services
