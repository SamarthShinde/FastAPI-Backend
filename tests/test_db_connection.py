import os
import sys
from sqlalchemy import text
from DB.database import engine, SessionLocal
from DB.models import User, UserSettings

def test_database_connection():
    """Test database connection and basic operations."""
    print("\n🔍 Testing Database Connection")
    print("=" * 50)
    
    try:
        # Test 1: Basic connection
        print("\n1️⃣ Testing basic connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Basic connection successful!")
        
        # Test 2: Create test user
        print("\n2️⃣ Testing user creation...")
        db = SessionLocal()
        try:
            # Create a test user
            test_user = User(
                username="test_user",
                email="test@example.com",
                password_hash="test_hash"
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created successfully!")
            
            # Test 3: Create user settings
            print("\n3️⃣ Testing user settings creation...")
            test_settings = UserSettings(
                user_id=test_user.user_id,
                theme="light",
                preferred_model="Llama",
                language_preference="English"
            )
            db.add(test_settings)
            db.commit()
            print("✅ Test user settings created successfully!")
            
            # Test 4: Query the created data
            print("\n4️⃣ Testing data retrieval...")
            retrieved_user = db.query(User).filter(User.username == "test_user").first()
            if retrieved_user:
                print(f"✅ User retrieved: {retrieved_user.username}")
                print(f"✅ User settings: {retrieved_user.settings.theme}")
            else:
                print("❌ Failed to retrieve test user")
            
            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            db.delete(test_settings)
            db.delete(test_user)
            db.commit()
            print("✅ Test data cleaned up successfully!")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error during database operations: {str(e)}")
        finally:
            db.close()
            
        print("\n✅ All database tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run the tests
    test_database_connection() 