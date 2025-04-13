import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "src" / "frontend"
BACKEND_DIR = BASE_DIR / "src" / "backend"
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = ASSETS_DIR / "uploads"
IMAGES_DIR = ASSETS_DIR / "images"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sustainatrend")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/sustainatrend")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
WORKERS = int(os.getenv("WORKERS", "4"))

# File upload settings
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}

# AI Model settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Cache settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "sustainatrend")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Create necessary directories
for directory in [UPLOADS_DIR, IMAGES_DIR, BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True) 
# Trendsense API settings
TRENDSENSE_API_KEY = os.getenv("TRENDSENSE_API_KEY")
TRENDSENSE_API_URL = os.getenv("TRENDSENSE_API_URL", "https://api.trendsense.ai/v1")
