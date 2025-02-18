from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class GoogleTokenRequest(BaseModel):
    id_token: str

class OTPVerificationRequest(BaseModel):
    email: str
    otp: str

class ChatRequest(BaseModel):
    model_name: str
    message: str