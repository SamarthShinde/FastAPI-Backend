import os
from sqlalchemy import text
from DB.database import engine, Base
from DB.models import User, UserSettings, Conversation, Message, Subscription, Payment

def init_db():
    """Initialize the database with proper setup."""
    try:
        # Create all tables
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # For SQLite, enable foreign key constraints
        if "sqlite" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys = ON"))
                conn.commit()
                print("✅ SQLite foreign key constraints enabled")
        
        print("✅ Database initialization completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error during database initialization: {str(e)}")
        return False

if __name__ == "__main__":
    init_db()