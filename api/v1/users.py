from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from api.v1.captcha import get_captcha_store
from core.config import settings
from core.mail import send_verification_email, send_password_reset_email
from core.security import check_password_strength, get_password_hash, verify_password
from db.models import User, PasswordHistory
from schemas.user import (
    User as UserSchema, UserCreateWithCaptcha, PasswordChange,
    EmailSchema, PasswordReset
)

router = APIRouter()
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreateWithCaptcha,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new user, send verification email. User is inactive until verified.
    """
    captcha_store = get_captcha_store()
    correct_captcha_text = captcha_store.pop(user_in.captcha_id, None)
    if not correct_captcha_text or user_in.captcha_text.upper() != correct_captcha_text.upper():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect CAPTCHA text.")

    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered.")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    strength_check = check_password_strength(user_in.password)
    if strength_check["strength"] not in ["Strong", "Very Strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password is not strong enough: {strength_check['message']}",
        )

    hashed_password = get_password_hash(user_in.password)

    
    verification_token = str(uuid4())
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        password_changed_at=datetime.utcnow(),
        is_active=False,
        verification_token=verification_token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    
    db.add(new_user)
    db.flush() 
    history_entry = PasswordHistory(user_id=new_user.id, hashed_password=hashed_password)
    db.add(history_entry)
    db.commit()

    await send_verification_email(
        email_to=new_user.email,
        username=new_user.username,
        token=verification_token,
        background_tasks=background_tasks
    )
    
    return {"message": "Registration successful. Please check your email to verify your account."}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_user_email(token: str, db: Session = Depends(get_db)):
    """Verify user's email with the provided token."""
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")
    
    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already verified.")

    if datetime.utcnow() > user.verification_token_expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token has expired.")

    user.is_active = True
    user.verification_token = None
    user.verification_token_expires_at = None
    db.commit()

    return {"message": "Account verified successfully. You can now log in."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def request_password_reset(
    email_in: EmailSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a password reset link to the user's email."""
    user = db.query(User).filter(User.email == email_in.email).first()
    if user:
        reset_token = str(uuid4())
        user.verification_token = reset_token
        user.verification_token_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        # Send email in background
        await send_password_reset_email(
            email_to=user.email,
            username=user.username,
            token=reset_token,
            background_tasks=background_tasks
        )

    return {"message": "If an account with this email exists, a password reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def perform_password_reset(password_in: PasswordReset, db: Session = Depends(get_db)):
    """Reset user's password using a valid token."""
    user = db.query(User).filter(User.verification_token == password_in.token).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")
    if datetime.utcnow() > user.verification_token_expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token has expired.")

    strength_check = check_password_strength(password_in.new_password)
    if strength_check["strength"] not in ["Strong", "Very Strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New password is not strong enough: {strength_check['message']}",
        )
    
    new_hashed_password = get_password_hash(password_in.new_password)
    recent_passwords = user.password_history[:settings.PASSWORD_HISTORY_LIMIT]
    for old_pass in recent_passwords:
        if verify_password(password_in.new_password, old_pass.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password cannot be the same as one of your last {settings.PASSWORD_HISTORY_LIMIT} passwords."
            )
            
    user.hashed_password = new_hashed_password
    user.password_changed_at = datetime.utcnow()
    user.verification_token = None
    user.verification_token_expires_at = None
    
    new_history_entry = PasswordHistory(user_id=user.id, hashed_password=new_hashed_password)
    db.add(new_history_entry)
    db.commit()

    return {"message": "Password has been reset successfully. You can now log in."}


@router.get("/me", response_model=UserSchema)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Fetch the profile of the currently authenticated user.
    This endpoint serves to test authentication.
    """
    return current_user

@router.put("/me/change-password", status_code=status.HTTP_200_OK)
def change_current_user_password(
    password_in: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change the current user's password after performing all security checks.
    """
    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password.")

    strength_check = check_password_strength(password_in.new_password)
    if strength_check["strength"] not in ["Strong", "Very Strong"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New password is not strong enough: {strength_check['message']}",
        )

    new_hashed_password = get_password_hash(password_in.new_password)
    recent_passwords = current_user.password_history[:settings.PASSWORD_HISTORY_LIMIT]
    for old_pass in recent_passwords:
        if verify_password(password_in.new_password, old_pass.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password cannot be the same as one of your last {settings.PASSWORD_HISTORY_LIMIT} passwords."
            )

    current_user.hashed_password = new_hashed_password
    current_user.password_changed_at = datetime.utcnow()
    
    new_history_entry = PasswordHistory(user_id=current_user.id, hashed_password=new_hashed_password)
    db.add(new_history_entry)
    
    db.commit()
    
    return {"message": "Password updated successfully."}