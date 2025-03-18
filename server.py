import uvicorn
import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def setup_database():
    """Set up the database if it doesn't exist."""
    try:
        # Import the database modules
        from DB.database import engine
        from DB.models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
        return True
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

def main():
    """Run the API server."""
    print("Starting API server...")
    
    # Set up database
    if not setup_database():
        print("Failed to set up database. Exiting.")
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