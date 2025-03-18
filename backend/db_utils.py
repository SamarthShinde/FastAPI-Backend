from typing import Optional
from datetime import datetime
from DB.database import SessionLocal
from DB.models import User, Conversation, Message, UserSettings

def get_or_create_conversation(db, user_id: int, conversation_id: Optional[int] = None):
    """Get an existing conversation or create a new one if none exists."""
    if conversation_id:
        # Get specific conversation
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if conversation:
            return conversation
    
    # Get active conversation or create new one
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.status == "active"
    ).first()
    
    if not conversation:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            status="active"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation

def save_message(db, conversation_id: int, user_id: int, role: str, message_text: str, 
                response_time_ms: Optional[int] = None):
    """Save a message to the database."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        message_text=message_text,
        timestamp=datetime.now(),
        response_time_ms=response_time_ms
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

def get_user_settings(db, user_id: int):
    """Get user settings or create default settings if none exist."""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()
    
    if not settings:
        # Create default settings
        settings = UserSettings(
            user_id=user_id,
            theme="light",
            preferred_model="Llama",
            language_preference="English",
            notifications_enabled=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings 