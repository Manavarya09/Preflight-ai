"""
Database connection management for PreFlight AI
"""
import os
from contextlib import contextmanager
from typing import Generator

import redis
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool

# Database URLs from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://preflight:password@localhost:5432/preflight_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# PostgreSQL Engine Configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Maximum number of connections in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging during development
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis Connection
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
)


# ============================================================================
# PostgreSQL Session Management
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.
    
    Usage:
        @app.get("/flights")
        def get_flights(db: Session = Depends(get_db)):
            return db.query(FlightHistory).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI routes.
    
    Usage:
        with get_db_context() as db:
            flights = db.query(FlightHistory).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Redis Connection Management
# ============================================================================


def get_redis():
    """
    Get Redis client for caching operations.
    
    Returns:
        redis.Redis: Redis client instance
    """
    return redis_client


def test_redis_connection() -> bool:
    """
    Test Redis connection.
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        return redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


# ============================================================================
# Connection Event Handlers
# ============================================================================


@event.listens_for(Pool, "connect")
def set_postgresql_pragma(dbapi_conn, connection_record):
    """
    Set PostgreSQL connection parameters when connection is created.
    """
    cursor = dbapi_conn.cursor()
    # Set application name for easier debugging
    cursor.execute("SET application_name TO 'preflight_ai_backend'")
    # Set search path
    cursor.execute("SET search_path TO public")
    cursor.close()


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Called when connection is retrieved from the pool.
    Can be used for logging or monitoring.
    """
    pass


# ============================================================================
# Database Initialization
# ============================================================================


def init_db():
    """
    Initialize database tables.
    Only call this during initial setup or in tests.
    """
    from database.models import Base

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_all_tables():
    """
    Drop all database tables.
    WARNING: Only use in development/testing!
    """
    from database.models import Base

    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped")


def test_db_connection() -> bool:
    """
    Test PostgreSQL database connection.
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# ============================================================================
# Health Check
# ============================================================================


def check_connections():
    """
    Check all database connections and return status.
    
    Returns:
        dict: Status of PostgreSQL and Redis connections
    """
    return {
        "postgresql": {
            "connected": test_db_connection(),
            "url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "unknown",
        },
        "redis": {
            "connected": test_redis_connection(),
            "url": REDIS_URL.split("@")[1] if "@" in REDIS_URL else "unknown",
        },
    }


# ============================================================================
# Export for easy imports
# ============================================================================

__all__ = [
    "engine",
    "SessionLocal",
    "redis_client",
    "get_db",
    "get_db_context",
    "get_redis",
    "init_db",
    "drop_all_tables",
    "test_db_connection",
    "test_redis_connection",
    "check_connections",
]
