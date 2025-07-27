"""
Configuration settings for RABuddy
"""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

# Data directories
PDF_DIR = PROJECT_ROOT / "pdfs"
CHROMA_PERSIST_DIR = BACKEND_ROOT / "chroma_store"
LOGS_DIR = BACKEND_ROOT / "logs"

# RAG settings
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "deepseek/deepseek-chat"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 5

# API settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 500

# Flask settings
DEFAULT_PORT = 5000
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://*.vercel.app"
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
OPENROUTER_API_KEY = get_env_var("OPENROUTER_API_KEY")
SUPABASE_URL = get_env_var("SUPABASE_URL")
SUPABASE_KEY = get_env_var("SUPABASE_KEY")
FLASK_SECRET_KEY = get_env_var("FLASK_SECRET_KEY", "dev-secret-key")

# Development vs Production
IS_DEVELOPMENT = get_env_var("FLASK_ENV") == "development"
IS_PRODUCTION = not IS_DEVELOPMENT
