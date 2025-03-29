from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from pydantic import BaseModel, model_validator, ValidationError
import sqlite3
from typing import Optional
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
db_path = ROOT_DIR / "backend" / "data.db"

router = APIRouter()

# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
def get_db():
    db_path = db_path
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @model_validator(mode="before")
    @classmethod
    def check_email_or_username(cls, values):
        """Ensure that exactly one of (email OR username) is provided."""
        email = values.get("email")
        username = values.get("username")

        if not email and not username:
            raise ValueError("Either email or username must be provided")
        
        if email and username:
            raise ValueError("Provide only email OR username, not both")
        
        return values


@router.post("/register")
def register(user: UserCreate, db=Depends(get_db)):
    """Register a new user with email, username and a hashed password"""
    email = user.email.strip().lower()
    username = user.username.strip()
    hashed_password = pwd_context.hash(user.password)

    try:
        db.execute("INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)", (email, username, hashed_password)),
        db.commit()
        user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
        return {"message": "User registered successfully", "user_id": user_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email or username already exists")
    finally:
        db.close()
    
@router.post("/login")
def login(user: UserLogin, db=Depends(get_db)):
    """Authenticate user using either case-insensitive email OR case-sensitive username and verify password"""

    if bool(user.email) == bool(user.username):  # XOR logic: one must be provided, not both
        raise HTTPException(status_code=400, detail="Provide either email OR username, not both")

    if user.email:  # Case-insensitive email login
        user_db = db.execute(
            "SELECT * FROM users WHERE LOWER(email) = ?", 
            (user.email.strip().lower(),)
        ).fetchone()
    elif user.username:  # Case-sensitive username login
        user_db = db.execute(
            "SELECT * FROM users WHERE username = ?", 
            (user.username.strip(),)
        ).fetchone()
    else:
        raise HTTPException(status_code=400, detail="Provide either email or username")

    db.close()

    if not user_db or not pwd_context.verify(user.password, user_db["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Debugging: Print login response
    print(f"✅ Debug: User logged in: {dict(user_db)}")

    return {        
        "message": "Login successful",
        "user_id": user_db["id"],  # Ensure `user_id` is returned
        "email": user_db["email"],
        "username": user_db["username"]
    }
