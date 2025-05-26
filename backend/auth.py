from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import bcrypt
import jwt
import threading
import time
from DB.database import SessionLocal
from DB.models import User
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.email_utils import generate_otp, send_otp_email

# In-memory OTP storage with expiry
otp_store = {}
otp_lock = threading.Lock()
OTP_EXPIRY_SECONDS = 600  # 10 minutes

# Background thread to clean expired OTPs
def cleanup_expired_otps():
    while True:
        time.sleep(60)  # Check every minute
        current_time = time.time()
        with otp_lock:
            expired_keys = [k for k, v in otp_store.items() if v['expiry'] < current_time]
            for k in expired_keys:
                del otp_store[k]

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired_otps, daemon=True)
cleanup_thread.start()

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash of the password."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by email and password."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        
        # Update last login time
        user.last_login = datetime.now()
        db.commit()
        
        # Return user data as a dictionary
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    finally:
        db.close()

def create_user(username: str, email: str, password: str) -> User:
    """Create a new user."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise ValueError("Email already registered")
            else:
                raise ValueError("Username already taken")
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    finally:
        db.close()

def create_access_token(user_id: int) -> str:
    """Create a JWT access token for the user."""
    try:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Error in create_access_token: {str(e)}")
        raise e

def verify_token(token: str) -> Optional[int]:
    """Verify a JWT token and return the user_id if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except jwt.PyJWTError:
        return None

def send_otp_for_email(email: str) -> Tuple[bool, str]:
    """Send OTP to the specified email for verification."""
    # Check if email exists in the database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "Email not registered"
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in memory with expiry
        expiry_time = time.time() + OTP_EXPIRY_SECONDS
        with otp_lock:
            otp_store[email] = {
                'otp': otp,
                'expiry': expiry_time
            }
        
        # Send OTP via email
        email_sent = send_otp_email(email, otp)
        if not email_sent:
            return False, "Failed to send OTP email"
        
        return True, "OTP sent successfully"
    finally:
        db.close()

def verify_otp(email: str, otp: str) -> Tuple[bool, Optional[User], str]:
    """Verify the OTP for the given email."""
    try:
        # Get stored OTP from memory
        with otp_lock:
            stored_data = otp_store.get(email)
        
        if not stored_data:
            return False, None, "OTP expired or not found"
        
        if time.time() > stored_data['expiry']:
            with otp_lock:
                if email in otp_store:
                    del otp_store[email]
            return False, None, "OTP expired"
        
        if otp != stored_data['otp']:
            return False, None, "Invalid OTP"
        
        # OTP is valid, delete it from memory
        with otp_lock:
            if email in otp_store:
                del otp_store[email]
        
        # Get user from database
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False, None, "User not found"
            
            # Update last login time
            user.last_login = datetime.now()
            db.commit()
            
            # Create a detached copy of the user to avoid SQLAlchemy issues
            user_dict = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'last_login': user.last_login
            }
            
            # Create a new User instance with the copied data
            detached_user = User(
                user_id=user_dict['user_id'],
                username=user_dict['username'],
                email=user_dict['email'],
                role=user_dict['role'],
                last_login=user_dict['last_login']
            )
            
            return True, detached_user, "OTP verified successfully"
        finally:
            db.close()
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        return False, None, f"Error verifying OTP: {str(e)}"

def register_with_otp(username: str, email: str, password: str) -> Tuple[bool, str]:
    """Register a new user and send OTP for verification."""
    try:
        # Create user
        user = create_user(username, email, password)
        
        # Skip OTP verification for now
        return True, "User registered successfully."
        
        # Commented out OTP verification for now
        # success, message = send_otp_for_email(email)
        # if not success:
        #     return False, message
        # return True, "User registered. OTP sent for verification."
    except ValueError as e:
        return False, str(e) 
