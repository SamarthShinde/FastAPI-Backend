import uvicorn
import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
logger.info("Added %s to Python path", current_dir)

# Load environment variables from the correct path
env_path = os.path.join(current_dir, "backend", ".env")
load_dotenv(dotenv_path=env_path)
logger.info("Loaded environment variables from %s", env_path)

def setup_database():
    """Set up the database if it doesn't exist."""
    try:
        # Import the database modules
        from DB.init_db import init_db
        
        logger.info("🔧 Setting up database...")
        logger.info("📡 Current working directory: %s", os.getcwd())
        
        # Initialize database
        if not init_db():
            logger.error("❌ Failed to initialize database")
            return False
            
        logger.info("✅ Database setup completed successfully")
        return True
    except Exception as e:
        logger.error("❌ Error setting up database: %s", str(e))
        return False

def main():
    """Run the API server."""
    logger.info("🚀 Starting API server...")
    
    # Set up database
    if not setup_database():
        logger.error("❌ Failed to set up database. Exiting.")
        sys.exit(1)
    
    try:
        # Import the app
        from backend.api import app
        logger.info("✅ Successfully imported API app")
        
        # Run the app
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="debug"
        )
    except Exception as e:
        logger.error("❌ Error starting server: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 