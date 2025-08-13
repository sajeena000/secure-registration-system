from datetime import datetime, timedelta
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request 
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.config import settings
from db.base import SessionLocal
from db.models import User
from schemas.token import TokenData

def get_token_from_cookie(request: Request) -> Optional[str]:
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        return token.split("Bearer ")[1]
    return None

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(get_token_from_cookie)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    if datetime.utcnow() > user.password_changed_at + timedelta(days=settings.PASSWORD_LIFESPAN_DAYS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password has expired. Please change your password.",
        )
    
    return user


def redirect_if_authenticated(
    token: Optional[str] = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
):
    """
    A dependency that checks for an authentication cookie.
    If a valid cookie for an existing user is found, it raises an
    HTTPException that triggers a 307 Temporary Redirect to the /profile page.
    """
    if token is None:
        return

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return
        
        user = db.query(User).filter(User.username == username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/profile"},
            )
    except JWTError:
        return
    
def get_current_user_or_redirect(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """
    A dependency that enforces authentication for a page.
    It attempts to get the current user from the access token cookie.
    - If successful, it returns the user object.
    - If the token is missing, invalid, or the user doesn't exist,
      it raises an HTTPException that triggers a 307 redirect to the login page.
    """
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/unauthorized"}, 
        )

    try:
        token_value = token.split("Bearer ")[1]
        payload = jwt.decode(
            token_value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=307, headers={"Location": "/unauthorized"})

    except (JWTError, IndexError):
        raise HTTPException(status_code=307, headers={"Location": "/unauthorized"})

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=307, headers={"Location": "/unauthorized"})
    
    if datetime.utcnow() > user.password_changed_at + timedelta(days=settings.PASSWORD_LIFESPAN_DAYS):
        raise HTTPException(status_code=307, headers={"Location": "/unauthorized"})

    return user