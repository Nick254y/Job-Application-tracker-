"""Authentication routes for DocFlow Marketplace."""

import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import User, Payment, SessionLocal
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security settings
JWT_SECRET = "docflow_marketplace_secret_key_2024_very_secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "client"


class UserLogin(BaseModel):
    username: str
    password: str
    email: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str
    role: str


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, email: str, username: str, role: str) -> str:
    """Create a JWT access token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token: str = None):
    """Dependency to get the current authenticated user."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_token(token)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=dict)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = hash_password(user.password)
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return user without password hash
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role,
        "message": "Account created successfully. Please log in.",
    }


@router.post("/signin", response_model=dict)
async def signin(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user:
        db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="Account is deactivated")
    
    # Create JWT token
    token = create_token(
        user_id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role,
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role,
        "message": "Login successful",
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token is invalidated automatically).
    Returns a simple confirmation.
    """
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """
    Get the current authenticated user.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }
