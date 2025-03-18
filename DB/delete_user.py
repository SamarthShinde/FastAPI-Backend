import sys
import os
import argparse

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from DB.database import SessionLocal
from DB.models import User, Conversation, Message

def delete_user_by_email(email, force=False):
    """Delete a user from the database by email."""
    db = SessionLocal()
    try:
        # Find the user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User with email '{email}' not found.")
            return False
        
        # Print user info
        print(f"Found user: ID={user.user_id}, Username={user.username}, Email={user.email}")
        
        # If not force mode, ask for confirmation
        if not force:
            confirm = input(f"Are you sure you want to delete user '{user.username}' (y/n)? ")
            if confirm.lower() != 'y':
                print("Deletion cancelled.")
                return False
        
        # Find all conversations
        conversations = db.query(Conversation).filter(Conversation.user_id == user.user_id).all()
        
        # Delete all messages in those conversations
        for conversation in conversations:
            deleted_messages = db.query(Message).filter(
                Message.conversation_id == conversation.conversation_id
            ).delete()
            print(f"Deleted {deleted_messages} messages from conversation {conversation.conversation_id}")
        
        # Delete all conversations
        deleted_convs = db.query(Conversation).filter(
            Conversation.user_id == user.user_id
        ).delete()
        print(f"Deleted {deleted_convs} conversations")
        
        # Delete user
        db.delete(user)
        db.commit()
        print(f"Successfully deleted user {user.username} ({user.email})")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a user from the database by email")
    parser.add_argument("email", help="Email of the user to delete")
    parser.add_argument("-f", "--force", action="store_true", help="Delete without confirmation")
    args = parser.parse_args()
    
    success = delete_user_by_email(args.email, args.force)
    if not success:
        sys.exit(1) 