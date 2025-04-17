from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Text, DECIMAL
from sqlalchemy.orm import relationship
from DB.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    role = Column(Enum("admin", "user", "premium user"), default="user")
    conversations = relationship("Conversation", back_populates="user")
    settings = relationship("UserSettings", back_populates="user")

class UserSettings(Base):
    __tablename__ = "User_Settings"
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    theme = Column(Enum("light", "dark"), default="light")
    preferred_model = Column(String(50), default="llama3.2:3b")
    language_preference = Column(String(50), default="English")
    notifications_enabled = Column(Boolean, default=True)
    user = relationship("User", back_populates="settings")

class Conversation(Base):
    __tablename__ = "Conversations"
    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("active", "archived"), default="active")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "Messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("Conversations.conversation_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    role = Column(Enum("user", "assistant", "system"), nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=True)
    conversation = relationship("Conversation", back_populates="messages")

class Subscription(Base):
    __tablename__ = "Subscriptions"
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    plan = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=False)
    last_payment_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="subscription")

class Payment(Base):
    __tablename__ = "Payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    payment_id = Column(String(100), unique=True, nullable=False)
    order_id = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="pending")
    payment_method = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user = relationship("User", backref="payments")