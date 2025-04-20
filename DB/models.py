from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, DECIMAL, Index
from sqlalchemy import Table, MetaData, Enum as SQLEnum, event, inspect, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import expression
from .base import Base
from datetime import datetime
import enum
import logging

logger = logging.getLogger(__name__)
# Define enum classes for type safety and validation
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM_USER = "premium user"
    
class ConversationStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    
class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    
class ThemeType(enum.Enum):
    LIGHT = "light"
    DARK = "dark"

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    @classmethod
    def not_deleted(cls):
        """Query filter for not deleted records."""
        return cls.is_deleted == False

class TimestampMixin:
    """Mixin for adding created and updated timestamps."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    # Remove unique=True from columns and define constraints at table level
    username = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Define constraints and indexes explicitly
    __table_args__ = (
        # Named unique constraints
        UniqueConstraint('username', name='uq_users_username'),
        UniqueConstraint('email', name='uq_users_email'),
        {'sqlite_autoincrement': True}
    )
    # Relationships with cascade delete
    conversations = relationship(
        "Conversation", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"  # Dynamic loading for better performance with many conversations
    )
    
    settings = relationship(
        "UserSettings", 
        back_populates="user", 
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan",
        lazy="joined"  # Eager loading for settings as they're frequently accessed
    )
    
    messages = relationship(
        "Message", 
        back_populates="user",
        cascade="all, delete-orphan", 
        lazy="dynamic"
    )
    
    subscriptions = relationship(
        "Subscription", 
        back_populates="user",
        cascade="all, delete-orphan", 
        lazy="select"
    )
    
    payments = relationship(
        "Payment", 
        back_populates="user",
        cascade="all, delete-orphan", 
        lazy="dynamic"
    )
    
    # Validations
    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username
    
    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email format")
        return email
    def soft_delete(self):
        """Soft delete the user and all related entities."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        logger.info(f"User {self.user_id} soft deleted at {self.deleted_at}")
        return True

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

class UserSettings(Base, TimestampMixin):
    __tablename__ = "User_Settings"
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", name="fk_user_settings_user_id"), nullable=False, index=True)
    theme = Column(SQLEnum(ThemeType), default=ThemeType.LIGHT, nullable=False)
    preferred_model = Column(String(50), default="llama3.2:3b", nullable=False)
    language_preference = Column(String(50), default="English", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    
    user = relationship("User", back_populates="settings")
    
    @validates('preferred_model')
    def validate_model(self, key, model):
        if not model or len(model) < 1:
            return "llama3.2:3b"  # Default model if invalid
        return model
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, theme='{self.theme}', model='{self.preferred_model}')>"

# Create an index for user settings lookup with explicit name
Index('idx_user_settings_user_id', UserSettings.user_id)

class Conversation(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "Conversations"
    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", name="fk_conversation_user_id"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation", nullable=False)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", 
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="dynamic",  # Dynamic loading for better performance with many messages
        order_by="Message.timestamp.asc()"  # Order messages by timestamp
    )
    
    def soft_delete(self):
        """Soft delete the conversation."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.status = ConversationStatus.ARCHIVED
        logger.info(f"Conversation {self.conversation_id} soft deleted at {self.deleted_at}")
        return True
    
    def message_count(self):
        """Get the count of messages in this conversation."""
        return self.messages.count()
    
    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, user_id={self.user_id}, status='{self.status}')>"

# Create an index for conversation lookup by user and status with explicit name
Index('idx_conversations_user_status', Conversation.user_id, Conversation.status)

class Message(Base, TimestampMixin):
    __tablename__ = "Messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("Conversations.conversation_id", ondelete="CASCADE", name="fk_message_conversation_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="SET NULL", name="fk_message_user_id"), nullable=True, index=True)
    role = Column(SQLEnum(MessageRole), nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
    
    @validates('message_text')
    def validate_message(self, key, text):
        if not text or text.strip() == '':
            raise ValueError("Message text cannot be empty")
        return text
    
    def __repr__(self):
        return f"<Message(id={self.message_id}, conversation_id={self.conversation_id}, role='{self.role}')>"
# Create indexes for message queries with explicit names
Index('idx_messages_by_conversation', Message.conversation_id, Message.timestamp)
Index('idx_messages_by_user', Message.user_id)

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Subscription(Base, TimestampMixin):
    __tablename__ = "Subscriptions"
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", name="fk_subscription_user_id"), nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True, index=True)
    auto_renew = Column(Boolean, default=False, nullable=False)
    last_payment_id = Column(String(100), nullable=True)
    
    # Define the relationship with User
    user = relationship("User", back_populates="subscriptions")
    
    # Add constraint to ensure start_date is before expiry_date
    __table_args__ = (
        CheckConstraint('start_date <= expiry_date OR expiry_date IS NULL', name='ck_subscriptions_date_order'),
        {'sqlite_autoincrement': True}
    )
    @validates('plan')
    def validate_plan(self, key, plan):
        if isinstance(plan, str) and plan not in [p.value for p in SubscriptionPlan]:
            raise ValueError(f"Invalid subscription plan: {plan}")
        return plan
    
    def is_expired(self):
        """Check if the subscription is expired."""
        return datetime.utcnow() > self.expiry_date
    
    def __repr__(self):
        return f"<Subscription(id={self.subscription_id}, user_id={self.user_id}, plan='{self.plan}', active={self.is_active})>"

class Payment(Base, TimestampMixin):
    __tablename__ = "Payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id", ondelete="CASCADE", name="fk_payment_user_id"), nullable=False, index=True)
    # Columns with constraints defined at table level
    payment_id = Column(String(100), nullable=False)
    order_id = Column(String(100), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="payments")
    
    # Define table arguments for this model
    __table_args__ = (
        UniqueConstraint('payment_id', name='uq_payments_payment_id'),
        UniqueConstraint('order_id', name='uq_payments_order_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"
