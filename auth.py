from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
import random
import os

from database import get_db
from models import User
from otp_utils import send_otp_email  # Updated import
from config import GOOGLE_CLIENT_ID, SECRET_KEY, ALGORITHM

router = APIRouter()

# --------------------------
# SCHEMAS (No changes)
# --------------------------
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleSignInRequest(BaseModel):
    id_token: str

class EmailRegisterRequest(BaseModel):
    email: str
    username: str

class OTPPasswordRequest(BaseModel):
    email: str
    otp: str
    password: str
    confirm_password: str

class OTPVerificationRequest(BaseModel):
    email: str
    otp: str

# --------------------------
# PASSWORD HASHING (No changes)
# --------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --------------------------
# UPDATED EMAIL REGISTRATION FLOW
# --------------------------
@router.post("/auth/email-register")
def email_register(request: EmailRegisterRequest, db: Session = Depends(get_db)):
    if not request.email.lower().endswith("@gmail.com"):
        raise HTTPException(status_code=400, detail="Email must be a Gmail address")
    
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists. Please log in.")
    
    user = User(
        email=request.email,
        username=request.username,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    otp_code = str(random.randint(100000, 999999))
    user.otp_code = otp_code
    user.otp_created_at = datetime.utcnow()
    db.commit()
    
    # Updated OTP sending with status check
    if not send_otp_email(user.email, otp_code):
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    
    return {"message": "Registration initiated. OTP sent to your email. Please verify and set your password."}

# --------------------------
# REST OF THE ENDPOINTS (No changes)
# --------------------------
@router.post("/auth/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(request.password)
    new_user = User(username=request.username, email=request.email, hashed_password=hashed_password, is_verified=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/auth/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/email-register-complete")
def complete_email_register(request: OTPPasswordRequest, db: Session = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.otp_code or user.otp_code != request.otp:
        raise HTTPException(status_code=400, detail="Invalid or missing OTP")
    
    if datetime.utcnow() > user.otp_created_at + timedelta(minutes=10):
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    user.hashed_password = hash_password(request.password)
    user.is_verified = True
    user.otp_code = None
    user.otp_created_at = None
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/google")
def google_login_register(payload: GoogleSignInRequest, db: Session = Depends(get_db)):
    try:
        id_info = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        email = id_info["email"]
        google_user_id = id_info["sub"]
        username = id_info.get("name", email.split("@")[0])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google ID token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            username=username,
            google_id=google_user_id,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}