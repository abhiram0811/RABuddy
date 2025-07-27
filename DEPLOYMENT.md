# RABuddy Development and Deployment Guide

## Development Environment

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git
- OpenRouter API key (free tier available)

### Quick Setup
Run the setup script for your platform:
- **Windows**: `setup.bat`
- **Linux/Mac**: `./setup.sh`

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app.py
```

#### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## API Keys Required

### OpenRouter (Required)
1. Sign up at https://openrouter.ai
2. Get your API key from the dashboard
3. Add to `backend/.env`:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

### Supabase (Optional - for cloud logging)
1. Create a project at https://supabase.com
2. Get URL and anon key from project settings
3. Run the SQL schema from `supabase_schema.sql`
4. Add to `backend/.env`:
   ```
   SUPABASE_URL=your_url_here
   SUPABASE_KEY=your_key_here
   ```

## Deployment

### Backend - Render

1. **Create Render Account**: https://render.com
2. **Connect Repository**: Link your GitHub repo
3. **Create Web Service**:
   - Name: `rabuddy-backend`
   - Environment: `Docker`
   - Instance Type: `Free`
   - Auto-Deploy: `Yes`

4. **Environment Variables**:
   ```
   OPENROUTER_API_KEY=your_key
   SUPABASE_URL=your_url (optional)
   SUPABASE_KEY=your_key (optional)
   FLASK_ENV=production
   ```

5. **Build Settings**:
   - Root Directory: `backend`
   - Build Command: `docker build -t rabuddy .`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Frontend - Vercel

1. **Create Vercel Account**: https://vercel.com
2. **Import Project**: Connect your GitHub repo
3. **Configure**:
   - Framework: `Next.js`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com/api
   ```

## File Structure

```
RABuddy/
├── backend/
│   ├── src/
│   │   ├── app.py              # Flask application
│   │   ├── routes.py           # API endpoints
│   │   ├── rag_engine.py       # Core RAG functionality
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   └── feedback_logger.py  # User feedback logging
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── .env.example           # Environment template
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   └── components/        # React components
│   ├── package.json           # Node.js dependencies
│   └── next.config.js         # Next.js configuration
├── pdfs/                      # PDF documents storage
├── supabase_schema.sql        # Database schema
├── setup.sh                  # Unix setup script
├── setup.bat                 # Windows setup script
└── README.md                 # Main documentation
```

## Adding Documents

1. Place PDF files in the `pdfs/` directory
2. Restart the backend server
3. The system will automatically process and index the documents

## Monitoring and Logs

### Backend Logs
- Local: `backend/logs/rabuddy.log`
- Render: View in Render dashboard

### Feedback Analytics
- Local: `backend/logs/feedback_*.jsonl`
- Supabase: Dashboard analytics

## Customization

### Change LLM Model
Edit `backend/src/rag_engine.py`:
```python
model="deepseek/deepseek-chat"  # Change to your preferred model
```

### Adjust Chunk Size
Edit `backend/src/pdf_processor.py`:
```python
def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
```

### Styling
Edit `frontend/tailwind.config.js` for custom colors and themes.

## Troubleshooting

### Common Issues

1. **PDF Processing Fails**
   - Ensure PDFs are not corrupted
   - Check file permissions
   - Review logs for specific errors

2. **ChromaDB Persistence Issues**
   - Verify `chroma_store` directory permissions
   - On Render, ensure persistent disk is configured

3. **API Rate Limits**
   - Monitor OpenRouter usage
   - Implement retry logic if needed

4. **CORS Errors**
   - Check frontend API URL configuration
   - Verify backend CORS settings

### Performance Optimization

1. **Vector Database**
   - Regularly clean up old embeddings
   - Monitor disk usage

2. **Response Times**
   - Cache frequently asked questions
   - Optimize chunk retrieval count

3. **Resource Usage**
   - Monitor memory usage on free tiers
   - Consider upgrading for heavy usage

## Security Considerations

1. **API Keys**: Never commit to version control
2. **CORS**: Configure for specific domains in production
3. **Rate Limiting**: Implement if needed for public access
4. **Data Privacy**: Ensure compliance with university policies

## Support

For technical issues:
1. Check logs for error messages
2. Review configuration files
3. Test with minimal setup
4. Contact development team

## Updates

To update the application:
1. Pull latest changes from repository
2. Update dependencies: `pip install -r requirements.txt` and `npm install`
3. Restart services
4. Monitor for any breaking changes
