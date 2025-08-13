import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Set up password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Function to check the strength of a password
def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Analyzes password strength based on multiple criteria, inspired by zxcvbn.
    - Checks length and character variety.
    - Provides a strength level and a descriptive, actionable feedback message.
    - "Strong" or "Very Strong" is required for registration.
    """
    length = len(password)
    feedback_items = []
    
    # Check if the password is long enough
    if length < 12:
        feedback_items.append("must be at least 12 characters long")

    # Check if it has different character types
    has_lowercase = bool(re.search(r"[a-z]", password))
    has_uppercase = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    
    char_types = sum([has_lowercase, has_uppercase, has_digit, has_symbol])
    
    # Note which types are missing
    missing_types = []
    if not has_lowercase: missing_types.append("lowercase letters")
    if not has_uppercase: missing_types.append("uppercase letters")
    if not has_digit: missing_types.append("numbers")
    if not has_symbol: missing_types.append("symbols")

    if missing_types:
        feedback_items.append(f"should include {', '.join(missing_types)}")
        
    # Assign strength level based on length and variety
    if length >= 12 and char_types == 4:
        if length >= 16:
            strength = "Very Strong"
        else:
            strength = "Strong"
    elif length >= 12 and char_types == 3:
        strength = "Moderate"
    elif length >= 8:
        strength = "Weak"
    else:
        strength = "Very Weak"

    # Create feedback message based on strength
    if strength == "Very Strong":
        message = "This is a very strong password."
    elif strength == "Strong":
        message = "This is a strong password. Make it 16+ characters for even better security."
    else:
        if feedback_items:
            message = f"Password is {strength.lower()}: it {', and '.join(feedback_items)}."
        else:
             message = f"Password is {strength.lower()} and does not meet all security requirements."

    return {"strength": strength, "message": message}