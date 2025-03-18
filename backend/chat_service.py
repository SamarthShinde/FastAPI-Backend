from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from DB.database import SessionLocal
from DB.models import User, Conversation, Message, UserSettings
from model.ai_agents import ChatAgent, available_models
from .db_utils import get_or_create_conversation, save_message, get_user_settings
from backend.payment_utils import check_user_subscription

class ChatService:
    """Service to handle chat interactions and database operations."""
    
    def __init__(self, user_id: int):
        """Initialize chat service for a specific user."""
        self.user_id = user_id
        self.db = SessionLocal()
        self.conversation = self._get_active_conversation()
        self.settings = self._get_user_settings()
        self.agent = self._create_agent()
    
    def _get_active_conversation(self) -> Conversation:
        """Get or create an active conversation for the user."""
        return get_or_create_conversation(self.db, self.user_id)
    
    def _get_user_settings(self) -> UserSettings:
        """Get user settings or create default settings."""
        settings = get_user_settings(self.db, self.user_id)
        if not settings:
            # Create default settings
            settings = UserSettings(
                user_id=self.user_id,
                theme="light",
                preferred_model=list(available_models.keys())[0]
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings
    
    def _create_agent(self) -> ChatAgent:
        """Create an AI agent based on user settings."""
        model_name = self.settings.preferred_model
        # If the preferred model isn't available, use the first available model
        if model_name not in available_models:
            model_name = list(available_models.keys())[0]
        return ChatAgent(model_name)
    
    def send_message(self, message_text: str) -> Dict[str, Any]:
        """Send a message and get a response from the AI."""
        # Get subscription info (using dummy implementation that always returns unlimited access)
        subscription = check_user_subscription(self.user_id)
        
        # Record start time for response timing
        start_time = time.time()
        
        # Save user message to database
        user_message = save_message(
            db=self.db,
            conversation_id=self.conversation.conversation_id,
            user_id=self.user_id,
            role="user",
            message_text=message_text
        )
        
        # Get context length from subscription
        context_length = subscription["details"].get("context_length", 20)
        
        # Get response from AI agent
        try:
            # Call the agent with context length
            response_text = self.agent.chat(
                message_text, 
                stream=False, 
                context_length=context_length
            )
            
            # If response is empty or contains an error message, use a fallback response
            if not response_text or response_text.startswith("Error"):
                response_text = "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."
        except Exception as e:
            response_text = "I'm sorry, I encountered an error while processing your request. Please try again later."
        
        # Calculate response time in milliseconds
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Save assistant message to database
        assistant_message = save_message(
            db=self.db,
            conversation_id=self.conversation.conversation_id,
            user_id=None,  # AI responses don't have a user_id
            role="assistant",
            message_text=response_text,
            response_time_ms=response_time_ms
        )
        
        return {
            "message_id": assistant_message.message_id,
            "content": response_text,
            "timestamp": assistant_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "response_time_ms": response_time_ms
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history for the current conversation."""
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == self.conversation.conversation_id)
            .order_by(Message.timestamp)
            .all()
        )
        
        return [
            {
                "message_id": msg.message_id,
                "role": msg.role,
                "content": msg.message_text,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "response_time_ms": msg.response_time_ms
            }
            for msg in messages
        ]
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations for the user."""
        conversations = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == self.user_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )
        
        return [
            {
                "conversation_id": conv.conversation_id,
                "created_at": conv.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": conv.status,
                # Get the first user message as the title (if any)
                "title": self._get_conversation_title(conv.conversation_id)
            }
            for conv in conversations
        ]
    
    def _get_conversation_title(self, conversation_id: int) -> str:
        """Get a title for the conversation based on the first user message."""
        first_message = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.role == "user"
            )
            .order_by(Message.timestamp)
            .first()
        )
        
        if first_message:
            # Truncate long messages
            title = first_message.message_text[:50]
            if len(first_message.message_text) > 50:
                title += "..."
            return title
        else:
            return f"Conversation {conversation_id}"
    
    def create_new_conversation(self) -> Dict[str, Any]:
        """Create a new conversation for the user."""
        # Set current conversation to inactive
        self.conversation.status = "archived"
        self.db.commit()
        
        # Create new conversation
        self.conversation = get_or_create_conversation(self.db, self.user_id)
        
        # Reset agent conversation history
        self.agent.conversation_history = []
        
        return {
            "conversation_id": self.conversation.conversation_id,
            "created_at": self.conversation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.conversation.status
        }
    
    def switch_conversation(self, conversation_id: int) -> bool:
        """Switch to a different conversation."""
        conversation = (
            self.db.query(Conversation)
            .filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == self.user_id
            )
            .first()
        )
        
        if not conversation:
            return False
        
        # Update current conversation
        self.conversation = conversation
        
        # Load conversation history into agent
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
            .all()
        )
        
        self.agent.conversation_history = [
            {
                "role": msg.role,
                "content": msg.message_text,
                "timestamp": msg.timestamp.strftime("%H:%M")
            }
            for msg in messages
        ]
        
        return True
    
    def update_model(self, model_name: str) -> bool:
        """Update the AI model being used."""
        if model_name not in available_models:
            return False
        
        # Update user settings
        self.settings.preferred_model = model_name
        self.db.commit()
        
        # Create new agent with selected model
        self.agent = ChatAgent(model_name)
        
        # Load conversation history into new agent
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == self.conversation.conversation_id)
            .order_by(Message.timestamp)
            .all()
        )
        
        self.agent.conversation_history = [
            {
                "role": msg.role,
                "content": msg.message_text,
                "timestamp": msg.timestamp.strftime("%H:%M")
            }
            for msg in messages
        ]
        
        return True
    
    def close(self):
        """Close the database session."""
        self.db.close() 