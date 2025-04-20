from typing import Optional, List, Dict, Any, Tuple, Union, TypeVar, Generic, Callable
from datetime import datetime, timedelta
import logging
import functools
import contextlib
from sqlalchemy import or_, and_, desc, asc, func, exc, text
from sqlalchemy.orm import Session, joinedload, contains_eager
from fastapi import HTTPException, status

from DB.database import SessionLocal, get_db_session, with_db_session, check_db_connection, retry_with_backoff
from DB.models import (
    User, Conversation, Message, UserSettings, Subscription, Payment,
    UserRole, ConversationStatus, MessageRole, SubscriptionPlan
)

logger = logging.getLogger(__name__)

# Define pagination result type
T = TypeVar('T')

class PaginationResult(Generic[T]):
    """Generic class for pagination results."""
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
        has_next: bool,
        has_prev: bool
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.pages = (total + page_size - 1) // page_size if total > 0 else 0
        self.has_next = has_next
        self.has_prev = has_prev

def paginate(query, page: int, page_size: int) -> PaginationResult:
    """Apply pagination to a query."""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
        
    # Calculate total and pages
    total = query.count()
    
    # Get items for current page
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Calculate has_next and has_prev
    has_next = (page * page_size) < total
    has_prev = page > 1
    
    return PaginationResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_prev=has_prev
    )

def validate_user_exists(db: Session, user_id: int) -> User:
    """Validate that a user exists and is not deleted."""
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        logger.error(f"User with ID {user_id} not found or is deleted")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found or is deleted"
        )
    return user

@with_db_session
def get_user_settings(session: Session, user_id: int) -> UserSettings:
    """Get user settings or create default settings if none exist."""
    try:
        # First validate that the user exists
        validate_user_exists(session, user_id)
        
        # Try to get existing settings with index
        settings = session.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        
        if not settings:
            # Create default settings
            logger.info(f"Creating default settings for user {user_id}")
            settings = UserSettings(
                user_id=user_id,
                theme="light",
                preferred_model="llama3.2:3b"
            )
            session.add(settings)
            session.commit()
            session.refresh(settings)
        
        return settings
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_user_settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving user settings"
        )

def get_or_create_conversation(
    session: Session,
    user_id: int,
    conversation_id: Optional[int] = None,
    title: str = "New Conversation"
) -> Conversation:
    """Get an existing conversation or create a new one."""
    try:
        # Validate that the user exists
        validate_user_exists(session, user_id)
        
        # If conversation_id is provided, try to get that specific conversation
        if conversation_id:
            conversation = session.query(Conversation).filter(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_deleted == False
            ).first()
            
            if conversation:
                # Update last activity
                conversation.last_activity = datetime.utcnow()
                session.commit()
                return conversation
            else:
                logger.warning(f"Conversation {conversation_id} for user {user_id} not found")
        
        # Get active conversation with proper enum value
        conversation = session.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.status == ConversationStatus.ACTIVE,
            Conversation.is_deleted == False
        ).order_by(desc(Conversation.last_activity)).first()
        
        if not conversation:
            # Create new conversation
            logger.info(f"Creating new conversation for user {user_id}")
            conversation = Conversation(
                user_id=user_id,
                status=ConversationStatus.ACTIVE,
                title=title,
                last_activity=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        
        return conversation
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_or_create_conversation: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while accessing conversation"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_or_create_conversation: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@with_db_session
def get_conversation_by_id(
    session: Session,
    conversation_id: int,
    user_id: int,
    include_messages: bool = False
) -> Optional[Conversation]:
    """Get a specific conversation by ID."""
    try:
        # Query conversation
        query = session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_deleted == False
        )
        
        # Eager load messages if requested
        if include_messages:
            query = query.options(
                joinedload(Conversation.messages.and_(Message.is_deleted == False))
            )
        
        conversation = query.first()
        
        if not conversation:
            logger.warning(f"Conversation {conversation_id} for user {user_id} not found")
            return None
        
        return conversation
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_conversation_by_id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while accessing conversation"
        )

@with_db_session
def get_conversations(
    session: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    status: Optional[ConversationStatus] = None,
    include_deleted: bool = False
) -> PaginationResult[Conversation]:
    """Get conversations with pagination."""
    try:
        # Validate user exists
        validate_user_exists(session, user_id)
        
        # Base query
        query = session.query(Conversation).filter(Conversation.user_id == user_id)
        
        # Apply status filter if provided
        if status is not None:
            query = query.filter(Conversation.status == status)
            
        # Apply deleted filter unless specifically including deleted
        if not include_deleted:
            query = query.filter(Conversation.is_deleted == False)
            
        # Order by last activity
        query = query.order_by(desc(Conversation.last_activity))
        
        # Apply pagination
        return paginate(query, page, page_size)
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving conversations"
        )

@with_db_session
def save_message(
    session: Session,
    conversation_id: int,
    user_id: int,
    role: Union[MessageRole, str],
    message_text: str,
    response_time_ms: Optional[int] = None,
    token_count: Optional[int] = None,
    model_used: Optional[str] = None
) -> Message:
    """Save a message to the database with transaction handling."""
    try:
        # Validate parameters
        if not message_text or message_text.strip() == '':
            raise ValueError("Message text cannot be empty")
            
        # Convert string role to Enum if needed
        if isinstance(role, str):
            try:
                role = MessageRole[role.upper()]
            except KeyError:
                logger.error(f"Invalid message role: {role}")
                raise ValueError(f"Invalid message role: {role}")
        
        # Update conversation's last activity
        conversation = session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.is_deleted == False
        ).with_for_update().first()
        
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            raise ValueError(f"Conversation {conversation_id} not found")
            
        # Create the message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            message_text=message_text,
            timestamp=datetime.utcnow(),
            response_time_ms=response_time_ms,
            token_count=token_count,
            model_used=model_used
        )
        
        # Update conversation's last activity in the same transaction
        conversation.last_activity = datetime.utcnow()
        
        session.add(message)
        session.commit()
        session.refresh(message)
        
        return message
    except ValueError as e:
        logger.error(f"Validation error in save_message: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in save_message: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while saving message"
        )

@with_db_session
def get_conversation_messages(
    session: Session,
    conversation_id: int,
    user_id: int,
    page: int = 1,
    page_size: int = 50,
    newest_first: bool = False
) -> PaginationResult[Message]:
    """Get messages for a conversation with pagination."""
    try:
        # First check if conversation exists and belongs to user
        conversation = session.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_deleted == False
        ).first()
        
        if not conversation:
            logger.warning(f"Conversation {conversation_id} for user {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Query messages with proper ordering
        query = session.query(Message).filter(
            Message.conversation_id == conversation_id
        )
        
        # Order appropriately - default is oldest first for chat history
        if newest_first:
            query = query.order_by(desc(Message.timestamp))
        else:
            query = query.order_by(asc(Message.timestamp))
        
        # Apply pagination
        return paginate(query, page, page_size)
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error in get_conversation_messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving messages"
        )
