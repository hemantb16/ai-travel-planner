import logging
import time
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import DATABASE_URL, SQLITE_FALLBACK_URL

logger = logging.getLogger("travel_planner.database")

Base = declarative_base()

_engine = None
_SessionLocal = None
_active_db_type = "unknown"
_db_status = {"connected": False, "type": "none", "error": None, "url_masked": ""}

def _mask_url(url: str) -> str:
    if "@" in url:
        prefix, host_part = url.split("@", 1)
        scheme_user = prefix.split("//")[0] + "//***"
        return f"{scheme_user}@{host_part}"
    return url

def init_db():
    global _engine, _SessionLocal, _active_db_type, _db_status
    
    # Try PostgreSQL first
    try:
        logger.info(f"Attempting connection to PostgreSQL: {_mask_url(DATABASE_URL)}")
        pg_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "psycopg" in DATABASE_URL else {}
        )
        # Test connection
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            
        _engine = pg_engine
        _active_db_type = "postgresql"
        _db_status = {
            "connected": True,
            "type": "PostgreSQL",
            "error": None,
            "url_masked": _mask_url(DATABASE_URL)
        }
        logger.info("Successfully connected to PostgreSQL database.")
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to SQLite.")
        try:
            sqlite_engine = create_engine(
                SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
            with sqlite_engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            _engine = sqlite_engine
            _active_db_type = "sqlite"
            _db_status = {
                "connected": True,
                "type": "SQLite (Fallback)",
                "error": f"PostgreSQL unavailable: {str(e)[:80]}...",
                "url_masked": _mask_url(SQLITE_FALLBACK_URL)
            }
            logger.info("Successfully initialized SQLite fallback database.")
        except Exception as sqle:
            logger.error(f"Failed to initialize SQLite fallback: {sqle}")
            _db_status = {
                "connected": False,
                "type": "none",
                "error": str(sqle),
                "url_masked": ""
            }
            raise sqle

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    # Create tables
    try:
        Base.metadata.create_all(bind=_engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise e

def get_engine():
    global _engine
    if _engine is None:
        init_db()
    return _engine

def get_db() -> Generator[Session, None, None]:
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> dict:
    global _engine, _db_status
    if _engine is None:
        try:
            init_db()
        except Exception as e:
            return {"connected": False, "type": "offline", "error": str(e), "latency_ms": 0}

    t0 = time.time()
    try:
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        latency = round((time.time() - t0) * 1000, 1)
        return {
            "connected": True,
            "type": _db_status.get("type", "PostgreSQL"),
            "error": _db_status.get("error"),
            "latency_ms": latency,
            "url_masked": _db_status.get("url_masked")
        }
    except Exception as e:
        return {
            "connected": False,
            "type": _db_status.get("type", "unknown"),
            "error": str(e),
            "latency_ms": round((time.time() - t0) * 1000, 1)
        }
