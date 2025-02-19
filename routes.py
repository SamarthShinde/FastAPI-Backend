from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from auth import router as auth_router
from model_code import get_response, available_models
from models import ChatHistory, User
from schemas import ChatRequest
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, GOOGLE_CLIENT_ID
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
def chat(request: ChatRequest, background_tasks: BackgroundTasks, 
        db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """ Process user message & save chat history in background """
    # Collect all response chunks into a single string
    response_generator = get_response(request.model_name, request.message)
    full_response = "".join([chunk for chunk in response_generator])
    
    background_tasks.add_task(save_chat, user.id, request.model_name, 
                            request.message, full_response, db)
    return {"response": full_response}

def save_chat(user_id, model_used, message, response, db):
    """ Helper function to store chat asynchronously """
    chat_entry = ChatHistory(
        user_id=user_id,
        model_used=model_used,
        message=message,
        response=response
    )
    db.add(chat_entry)
    db.commit()

@router.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """ Fetch chat history of the logged-in user """
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).all()
    return {"history": [{
        "message": chat.message,
        "response": chat.response,
        "timestamp": chat.timestamp
    } for chat in chats]}

@router.get("/models")
def list_models():
    """ Fetch available models dynamically """
    return {"models": list(available_models.keys())}

# Removed duplicate Google endpoint - it's already properly implemented in auth.py