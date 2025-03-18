from fastapi import FastAPI, Depends, HTTPException, status, Header, Query, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, condecimal
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uvicorn
import json
from fastapi.responses import JSONResponse

from DB.database import SessionLocal
from DB.models import User, Conversation, Message, UserSettings, Subscription, Payment
from backend.auth import (
    authenticate_user, create_user, create_access_token, verify_token,
    send_otp_for_email, verify_otp, register_with_otp
)
from backend.chat_service import ChatService
from model.ai_agents import available_models
from backend.email_utils import send_welcome_email
from backend.api_dummy import router as dummy_router

app = FastAPI(title="Ollama Chat API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Models ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|user|premium user)$")

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    created_at: str
    last_login: Optional[str] = None

# --- OTP Auth Models ---

class EmailRequest(BaseModel):
    email: EmailStr

class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class RegisterOtpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

# --- Chat Models ---

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message_id: int
    content: str
    timestamp: str
    response_time_ms: Optional[int] = None

class ConversationInfo(BaseModel):
    conversation_id: int
    created_at: str
    status: str
    title: str

class ModelUpdate(BaseModel):
    model_name: str

# --- Settings Models ---

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")
    preferred_model: Optional[str] = None
    language_preference: Optional[str] = None
    notifications_enabled: Optional[bool] = None

class UserSettingsResponse(BaseModel):
    setting_id: int
    user_id: int
    theme: str
    preferred_model: str
    language_preference: str
    notifications_enabled: bool

# --- Subscription Models ---

class SubscriptionCreate(BaseModel):
    plan_name: str = Field(..., pattern="^(free|pro|enterprise)$")
    end_date: Optional[str] = None
    auto_renew: bool = False

class SubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, pattern="^(free|pro|enterprise)$")
    end_date: Optional[str] = None
    auto_renew: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    subscription_id: int
    user_id: int
    plan_name: str
    start_date: str
    end_date: Optional[str] = None
    auto_renew: bool

# --- Payment Models ---

class PaymentCreate(BaseModel):
    amount: condecimal(max_digits=10, decimal_places=2)
    currency: str = "USD"
    payment_gateway: str = Field(..., pattern="^(Stripe|Razorpay)$")

class PaymentUpdate(BaseModel):
    payment_status: str = Field(..., pattern="^(pending|completed|failed)$")

class PaymentResponse(BaseModel):
    payment_id: int
    user_id: int
    amount: float
    currency: str
    payment_status: str
    payment_gateway: str
    created_at: str

# --- Dependencies ---

async def get_current_user_id(authorization: str = Header(...)):
    """Get the current user ID from the authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth Routes ---

@app.post("/register", response_model=Dict[str, str])
async def register(user_data: RegisterOtpRequest):
    """Register a new user and send OTP for verification."""
    success, message = register_with_otp(
        user_data.username, 
        user_data.email, 
        user_data.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}

@app.post("/login", response_model=Dict[str, str])
async def login_request_otp(email_data: EmailRequest):
    """Request OTP for login."""
    success, message = send_otp_for_email(email_data.email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}

@app.post("/verify-otp", response_model=TokenResponse)
async def verify_otp_and_login(otp_data: OtpVerifyRequest):
    """Verify OTP and login user."""
    try:
        success, user, message = verify_otp(otp_data.email, otp_data.otp)
        
        if not success or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )
        
        # Generate access token
        access_token = create_access_token(user.user_id)
        
        # Send welcome email for new users (if last_login is None)
        if not user.last_login:
            send_welcome_email(user.email, user.username)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "username": user.username
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error in verify_otp_and_login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying OTP: {str(e)}"
        )

@app.post("/login/password", response_model=TokenResponse)
async def login_with_password(user_data: UserLogin):
    """Login a user with password (fallback method)."""
    user = authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user.user_id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username
    }

# --- User Routes ---

@app.get("/users/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Get current user information."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
    }

@app.put("/users/me", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Update current user information."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if username is being updated and is already taken
    if user_data.username and user_data.username != user.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username
    
    # Check if email is being updated and is already taken
    if user_data.email and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    # Only allow admin to change role
    if user_data.role and user.role == "admin":
        user.role = user_data.role
    
    db.commit()
    db.refresh(user)
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
    }

# --- Chat Routes ---

@app.post("/chat", response_model=MessageResponse)
async def send_message(
    message_data: MessageRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Send a message to the AI and get a response."""
    chat_service = ChatService(user_id)
    try:
        response = chat_service.send_message(message_data.message)
        return response
    finally:
        chat_service.close()

@app.get("/conversations", response_model=List[ConversationInfo])
async def get_conversations(user_id: int = Depends(get_current_user_id)):
    """Get all conversations for the user."""
    chat_service = ChatService(user_id)
    try:
        return chat_service.get_all_conversations()
    finally:
        chat_service.close()

@app.get("/conversations/current/messages", response_model=List[Dict[str, Any]])
async def get_current_conversation_messages(user_id: int = Depends(get_current_user_id)):
    """Get messages for the current conversation."""
    chat_service = ChatService(user_id)
    try:
        return chat_service.get_conversation_history()
    finally:
        chat_service.close()

@app.post("/conversations/new", response_model=Dict[str, Any])
async def create_new_conversation(user_id: int = Depends(get_current_user_id)):
    """Create a new conversation."""
    chat_service = ChatService(user_id)
    try:
        return chat_service.create_new_conversation()
    finally:
        chat_service.close()

@app.post("/conversations/{conversation_id}/switch")
async def switch_conversation(
    conversation_id: int = Path(..., description="The ID of the conversation to switch to"),
    user_id: int = Depends(get_current_user_id)
):
    """Switch to a different conversation."""
    chat_service = ChatService(user_id)
    try:
        success = chat_service.switch_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return {"status": "success"}
    finally:
        chat_service.close()

@app.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: int = Path(..., description="The ID of the conversation to archive"),
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Archive a conversation."""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.status = "archived"
    db.commit()
    
    return {"status": "success"}

@app.post("/models/update")
async def update_model(
    model_data: ModelUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """Update the AI model being used."""
    if model_data.model_name not in available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model not available. Available models: {', '.join(available_models.keys())}"
        )
    
    chat_service = ChatService(user_id)
    try:
        chat_service.update_model(model_data.model_name)
        return {"status": "success"}
    finally:
        chat_service.close()

@app.get("/models/available")
async def get_available_models():
    """Get a list of available models."""
    return {"models": list(available_models.keys())}

# --- Settings Routes ---

@app.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Get user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        # Create default settings
        settings = UserSettings(
            user_id=user_id,
            theme="light",
            preferred_model=list(available_models.keys())[0],
            language_preference="English",
            notifications_enabled=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "setting_id": settings.setting_id,
        "user_id": settings.user_id,
        "theme": settings.theme,
        "preferred_model": settings.preferred_model,
        "language_preference": settings.language_preference,
        "notifications_enabled": settings.notifications_enabled
    }

@app.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Update user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    if not settings:
        # Create default settings
        settings = UserSettings(
            user_id=user_id,
            theme="light",
            preferred_model=list(available_models.keys())[0],
            language_preference="English",
            notifications_enabled=True
        )
        db.add(settings)
    
    # Update settings
    if settings_data.theme is not None:
        settings.theme = settings_data.theme
    
    if settings_data.preferred_model is not None:
        if settings_data.preferred_model in available_models:
            settings.preferred_model = settings_data.preferred_model
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model not available. Available models: {', '.join(available_models.keys())}"
            )
    
    if settings_data.language_preference is not None:
        settings.language_preference = settings_data.language_preference
    
    if settings_data.notifications_enabled is not None:
        settings.notifications_enabled = settings_data.notifications_enabled
    
    db.commit()
    db.refresh(settings)
    
    return {
        "setting_id": settings.setting_id,
        "user_id": settings.user_id,
        "theme": settings.theme,
        "preferred_model": settings.preferred_model,
        "language_preference": settings.language_preference,
        "notifications_enabled": settings.notifications_enabled
    }

# --- Subscription Routes ---
# --- Payment Routes ---
# --- Admin Routes ---

@app.delete("/admin/users/delete-regular")
async def delete_regular_users(
    user_id: int = Depends(get_current_user_id),
    db: SessionLocal = Depends(get_db)
):
    """Delete all regular users (admin only)."""
    # Check if the current user is an admin
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    
    # Get count of users before deletion
    user_count = db.query(User).filter(User.role == "user").count()
    
    # Delete all users with role 'user'
    deleted = db.query(User).filter(User.role == "user").delete()
    
    # Commit the changes
    db.commit()
    
    return {
        "status": "success",
        "message": f"Successfully deleted {deleted} regular users",
        "deleted_count": deleted,
        "total_found": user_count
    }

# Include the dummy subscription and payment routes
# These provide API compatibility without implementing actual functionality
app.include_router(
    dummy_router,
    dependencies=[Depends(get_current_user_id)]
)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 