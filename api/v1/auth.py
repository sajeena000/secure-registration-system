from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.deps import get_db
from core.config import settings
from core.security import create_access_token, verify_password
from db.models import User

# Create a FastAPI router for authentication endpoints
router = APIRouter()

# --- LOGIN ENDPOINT ---
@router.post("/token", status_code=status.HTTP_200_OK)
def login_for_access_token(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Handles user login via a form submission (username and password).
    On successful authentication, it sets a secure, HttpOnly cookie
    containing the JWT access token and returns a success message.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not verified. Please check your email.",
        )

    # Generate a JWT with a unique identifier (JTI)
    jti = str(uuid4())
    access_token = create_access_token(data={"sub": user.username, "jti": jti})

    # Set the access token in a secure HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevents JS access
        samesite="lax",  # Good for security
        secure=False,  # Set to True in production with HTTPS
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    # Return success response
    return {"message": "Login successful"}

# --- LOGOUT ENDPOINT ---
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    """
    Logs out the user by clearing the access token cookie.
    """
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}