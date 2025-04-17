import uvicorn
import logging
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables from the correct path
env_path = os.path.join(current_dir, "backend", ".env")
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def setup_database():
    """Set up the database if it doesn't exist."""
    try:
        # Import the database modules
        from DB.init_db import init_db
        
        print("🔧 Setting up database...")
        print("📡 Current working directory:", os.getcwd())
        
        # Initialize database
        if not init_db():
            print("❌ Failed to initialize database")
            return False
            
        print("✅ Database setup completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return False

def main():
    """Run the API server."""
    print("🚀 Starting API server...")
    
    # Set up database
    if not setup_database():
        print("❌ Failed to set up database. Exiting.")
        sys.exit(1)
    
    # Import the app
    from backend.api import app
    
    # Run the app
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info"
    )

if __name__ == "__main__":
    main() 