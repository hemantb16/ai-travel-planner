import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PG_DATA_DIR = DATA_DIR / "pgdata"

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Settings
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres@127.0.0.1:5432/travel_planner"
)
SQLITE_FALLBACK_URL = os.getenv(
    "SQLITE_FALLBACK_URL", 
    f"sqlite:///{BASE_DIR / 'travel_planner.db'}"
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:latest")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
