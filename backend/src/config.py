"""
Configuration settings for RABuddy
"""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to main RABuddy directory
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

# Data directories
PDF_DIR = PROJECT_ROOT / "pdfs"
CHROMA_PERSIST_DIR = BACKEND_ROOT / "chroma_store"
LOGS_DIR = BACKEND_ROOT / "logs"

# Ensure directories exist
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# RAG settings
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "gemini-1.5-flash"  # Updated to use Gemini
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 8  # Increased for better context

# API settings  
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1000

# Flask settings
DEFAULT_PORT = int(os.getenv('PORT', 10000))  # Render uses PORT env var
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3006",
    "https://rabuddy-frontend.vercel.app",
    "https://rabuddy-5ncawvp74-abhiram-reddy-mulintis-projects.vercel.app",
    "https://rabuddy-oayjle78p-abhiram-reddy-mulintis-projects.vercel.app",
    "https://*.ngrok.io",
    "https://*.loca.lt",
    "*"  # Allow all origins for production testing
]

# ChromaDB settings
CHROMA_COLLECTION_NAME = "rabuddy_documents"

# Feedback settings
FEEDBACK_LOG_ROTATION = "10 MB"
FEEDBACK_LOG_RETENTION = "30 days"

# Environment variables with defaults
def get_env_var(key: str, default: str = "") -> str:
    """Get environment variable with default fallback"""
    return os.getenv(key, default)

# API Keys (from environment)
GEMINI_API_KEY = get_env_var("GEMINI_API_KEY")  # Updated for Gemini
OPENROUTER_API_KEY = get_env_var("OPENROUTER_API_KEY")  # Keep as fallback

def get_config():
    """Get configuration dictionary for the application"""
    return {
        'DEBUG': get_env_var('FLASK_ENV', 'development') == 'development',
        'SECRET_KEY': get_env_var('FLASK_SECRET_KEY', 'dev-secret-key'),
        'PORT': DEFAULT_PORT,
        'HOST': '0.0.0.0',
        'CORS_ORIGINS': CORS_ORIGINS,
        'GEMINI_API_KEY': GEMINI_API_KEY,
        'ENVIRONMENT': get_env_var('ENVIRONMENT', 'development')
    }
SUPABASE_URL = get_env_var("SUPABASE_URL")
SUPABASE_KEY = get_env_var("SUPABASE_KEY")
FLASK_SECRET_KEY = get_env_var("FLASK_SECRET_KEY", "dev-secret-key")

# Development vs Production
IS_DEVELOPMENT = get_env_var("FLASK_ENV") == "development"
IS_PRODUCTION = not IS_DEVELOPMENT
