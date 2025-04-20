from sqlalchemy import create_engine, event, exc, text
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool
import os
import sys
import time
import functools
import contextlib
from typing import Optional, Callable, Any
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus
from .models import UserSettings
from .base import Base  # Import Base from base.py

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Constants for database configuration
MAX_RETRY_COUNT = 5
RETRY_INITIAL_DELAY_SECONDS = 1
MAX_RETRY_DELAY_SECONDS = 60
DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_OVERFLOW = 10
DEFAULT_POOL_TIMEOUT = 30
DEFAULT_POOL_RECYCLE = 1800  # 30 minutes

# Load environment variables
env_path = os.path.join(project_root, "backend", ".env")
if not os.path.exists(env_path):
    logger.warning(f"⚠️ Warning: .env file not found at {env_path}")
    # Use default SQLite configuration
    DB_TYPE = "sqlite"
    DATABASE_URL = None
    POOL_SIZE = DEFAULT_POOL_SIZE
    MAX_OVERFLOW = DEFAULT_MAX_OVERFLOW
    POOL_TIMEOUT = DEFAULT_POOL_TIMEOUT
    POOL_RECYCLE = DEFAULT_POOL_RECYCLE
else:
    load_dotenv(dotenv_path=env_path)
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
    DATABASE_URL = os.getenv("DATABASE_URL")
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", DEFAULT_POOL_SIZE))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", DEFAULT_MAX_OVERFLOW))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", DEFAULT_POOL_TIMEOUT))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", DEFAULT_POOL_RECYCLE))

# Construct database URL based on database type
if DB_TYPE == "sqlite":
    # SQLite configuration with absolute path
    SQLITE_DB_PATH = os.path.join(project_root, "data", "app.db")
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"
    logger.info("📡 Using SQLite database at: %s", SQLITE_DB_PATH)
elif DB_TYPE in ["mysql", "mariadb"] and not DATABASE_URL:
    # Construct MySQL/MariaDB URL from individual components for better security
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "chatbot")
    DATABASE_URL = f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"📡 Using MySQL/MariaDB database on {DB_HOST}:{DB_PORT}")
elif DB_TYPE == "postgresql" and not DATABASE_URL:
    # Construct PostgreSQL URL from individual components for better security
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "chatbot")
    DATABASE_URL = f"postgresql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"📡 Using PostgreSQL database on {DB_HOST}:{DB_PORT}")
elif not DATABASE_URL:
    raise ValueError(f"DATABASE_URL is not set for {DB_TYPE} database type")

# Log database configuration (without sensitive info)
masked_url = DATABASE_URL
if "://" in DATABASE_URL and "@" in DATABASE_URL:
    # Mask password in URL for logging purposes
    parts = masked_url.split("://", 1)
    auth_url = parts[1].split("@", 1)
    user_pass = auth_url[0].split(":", 1)
    if len(user_pass) > 1:
        masked_url = f"{parts[0]}://{user_pass[0]}:****@{auth_url[1]}"

logger.info(f"📡 Database configuration: Type={DB_TYPE}, Pool Size={POOL_SIZE}, Max Overflow={MAX_OVERFLOW}")
logger.info(f"📡 Database URL: {masked_url}")
def retry_with_backoff(max_retries: int = MAX_RETRY_COUNT,
                      initial_delay: float = RETRY_INITIAL_DELAY_SECONDS,
                      max_delay: float = MAX_RETRY_DELAY_SECONDS,
                      backoff_factor: float = 2.0,
                      retryable_exceptions: tuple = (exc.OperationalError, exc.DatabaseError)):
    """Retry decorator with exponential backoff for database operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for retry_count in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    if retry_count >= max_retries:
                        logger.error(f"Maximum retry attempts ({max_retries}) reached. Giving up.")
                        raise
                    
                    logger.warning(f"Database operation failed: {str(e)}. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    
                    # Calculate next delay with exponential backoff
                    delay = min(delay * backoff_factor, max_delay)
        return wrapper
    return decorator

def get_engine_args():
    """Get appropriate engine arguments based on database type."""
    common_args = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_timeout": POOL_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
    }
    
    if DB_TYPE == "sqlite":
        # SQLite specific arguments
        return {
            "connect_args": {"check_same_thread": False},  # Required for SQLite
            "poolclass": QueuePool,  # Explicitly use QueuePool for SQLite
            "echo": os.getenv("SQL_ECHO", "false").lower() == "true",  # Only enable echo if explicitly set
        }
    elif DB_TYPE in ["mysql", "mariadb"]:
        # MySQL/MariaDB specific arguments
        return {
            **common_args,
            "pool_pre_ping": True,
            "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        }
    elif DB_TYPE == "postgresql":
        # PostgreSQL specific arguments
        return {
            **common_args,
            "pool_pre_ping": True,
            "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
        }
    else:
        # Default arguments for other database types
        return common_args

# Create engine with retry logic
@retry_with_backoff()
def create_db_engine():
    """Create and configure the database engine with retry logic."""
    engine_args = get_engine_args()
    logger.info(f"Creating database engine for {DB_TYPE} with pooling enabled")
    
    engine = create_engine(DATABASE_URL, **engine_args)
    
    # Set up event listeners for connection pool events
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        logger.debug("New database connection established")
    
    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_connection, connection_record, connection_proxy):
        logger.debug("Database connection checked out from pool")
    
    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_connection, connection_record):
        logger.debug("Database connection returned to pool")
    
    # Test connection with health check
    with engine.connect() as conn:
        if DB_TYPE == "sqlite":
            conn.execute(text("SELECT 1"))
        elif DB_TYPE in ["mysql", "mariadb"]:
            conn.execute(text("SELECT 1"))
        elif DB_TYPE == "postgresql":
            conn.execute(text("SELECT 1"))
        logger.info("✅ Successfully connected to the database and verified connection")
    
    return engine

# Create database engine with retry
try:
    engine = create_db_engine()
except Exception as e:
    logger.error(f"❌ Failed to create database engine after multiple retries: {str(e)}")
    raise

# Create sessionmaker with engine binding
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)
# Create scoped session for thread safety
ScopedSession = scoped_session(SessionLocal)

# Session management context manager
@contextlib.contextmanager
def get_db_session():
    """Context manager for database sessions to ensure proper cleanup."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()

def check_db_connection():
    """Check if database connection is healthy."""
    try:
        with get_db_session() as session:
            if DB_TYPE == "sqlite":
                session.execute(text("SELECT 1"))
            elif DB_TYPE in ["mysql", "mariadb"]:
                session.execute(text("SELECT 1"))
            elif DB_TYPE == "postgresql":
                session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

# Decorator for database operation retries
def with_db_session(func):
    """Decorator to provide a database session to a function."""
    @functools.wraps(func)
    @retry_with_backoff()
    def wrapper(*args, **kwargs):
        with get_db_session() as session:
            # Extract user_id from positional args
            user_id = args[0] if args else None
            # Ensure no duplicate session in kwargs
            kwargs.pop('session', None)
            # Pass parameters as keywords to avoid positional conflicts
            kwargs['user_id'] = user_id
            kwargs['session'] = session
            try:
                return func(**kwargs)
            except Exception as e:
                session.rollback()
                raise e
    return wrapper

@with_db_session
def get_user_settings(user_id: str, session: Session = None) -> Optional[UserSettings]:
    """Get user settings from the database."""
    try:
        return session.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        raise
