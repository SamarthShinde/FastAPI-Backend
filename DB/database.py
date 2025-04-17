from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
env_path = os.path.join(project_root, "backend", ".env")
if not os.path.exists(env_path):
    logger.warning(f"⚠️ Warning: .env file not found at {env_path}")
    # Use default SQLite configuration
    DB_TYPE = "sqlite"
    DATABASE_URL = None
else:
    load_dotenv(dotenv_path=env_path)
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DATABASE_URL = os.getenv("DATABASE_URL")

if DB_TYPE == "sqlite":
    # SQLite configuration with absolute path
    SQLITE_DB_PATH = os.path.join(project_root, "data", "app.db")
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"
    logger.info("📡 Using SQLite database at: %s", SQLITE_DB_PATH)
elif not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set for non-SQLite database")

logger.info("📡 FINAL DB URL BEING USED: %s", DATABASE_URL)

try:
    # Create engine with appropriate configuration
    if DB_TYPE == "sqlite":
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},  # Required for SQLite
            echo=True  # Enable SQL query logging for debugging
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Maximum number of connections that can be created above pool_size
            pool_timeout=30,  # Seconds to wait before giving up on getting a connection
            pool_recycle=1800  # Recycle connections after 30 minutes
        )
    
    # Test the connection
    with engine.connect() as conn:
        logger.info("✅ Successfully connected to the database")
except Exception as e:
    logger.error("❌ Failed to connect to database: %s", str(e))
    raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()