from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"  # **Fixed typo**
    
    id = Column(Integer, primary_key=True, index=True)  # **Changed to Integer**
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True)
    google_id = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)  # **Fixed typo**
    otp_code = Column(String, nullable=True)  # **Fixed typo**
    otp_created_at = Column(DateTime, nullable=True)  # **Fixed type**
    
    chat_history = relationship("ChatHistory", back_populates="user")  # **Fixed relationship**

class ChatHistory(Base):
    __tablename__ = "chat_history"  # **Fixed table name**
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))  # **Matched type to User.id**
    model_used = Column(String, nullable=False)
    message = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)  # **Fixed type**
    
    user = relationship("User", back_populates="chat_history")  # **Fixed relationship**