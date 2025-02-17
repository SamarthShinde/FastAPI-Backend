from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from auth import router as auth_router
from model_code import get_response, available_models
from models import ChatHistory, User
from schemas import ChatRequest
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, GOOGLE_CLIENT_ID, APPLE_BUNDLE_ID
import requests

# Include the auth routes you already have
router = APIRouter()
router.include_router(auth_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/chat")
def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """ Process user message & save chat history in background """
    response = get_response(request.model_name, request.message)
    background_tasks.add_task(save_chat, user.id, request.model_name, request.message, response, db)
    return {"response": response}

def save_chat(user_id, model_used, message, response, db):
    """ Helper function to store chat asynchronously """
    chat_entry = ChatHistory(user_id=user_id, model_used=model_used, message=message, response=response)
    db.add(chat_entry)
    db.commit()

@router.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """ Fetch chat history of the logged-in user """
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).all()
    return {"history": [{"message": chat.message, "response": chat.response, "timestamp": chat.timestamp} for chat in chats]}

@router.get("/models")
def list_models():
    """ Fetch available models dynamically """
    return {"models": list(available_models.keys())}

# --- New Endpoints for Social Login ---

from pydantic import BaseModel

class GoogleSignInRequest(BaseModel):
    id_token: str

@router.post("/auth/google")
def google_sign_in(request: GoogleSignInRequest, db: Session = Depends(get_db)):
    """
    Verifies the Google ID token from the client, upserts the user,
    and returns a JWT.
    """
    try:
        # Verify the token with Google's library
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
        id_info = google_id_token.verify_oauth2_token(request.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
        google_user_id = id_info["sub"]
        email = id_info["email"]
        name = id_info.get("name", "")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google ID token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=name or email.split("@")[0], email=email, google_id=google_user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

class AppleSignInRequest(BaseModel):
    apple_identity_token: str

APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"

@router.post("/auth/apple")
def apple_sign_in(request: AppleSignInRequest, db: Session = Depends(get_db)):
    """
    Verifies the Apple identity token from the client, upserts the user,
    and returns a JWT.
    """
    apple_keys = requests.get(APPLE_KEYS_URL).json()
    unverified_header = jwt.get_unverified_header(request.apple_identity_token)
    matching_key = None
    for key in apple_keys["keys"]:
        if key["kid"] == unverified_header["kid"]:
            matching_key = key
            break
    if not matching_key:
        raise HTTPException(status_code=400, detail="Invalid key ID from Apple token")
    
    try:
        decoded_payload = jwt.decode(request.apple_identity_token, matching_key, algorithms=["RS256"], audience=APPLE_BUNDLE_ID, issuer="https://appleid.apple.com")
        apple_user_id = decoded_payload["sub"]
        email = decoded_payload.get("email", "")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid Apple identity token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=email.split("@")[0], email=email, apple_id=apple_user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}