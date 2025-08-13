from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    password_changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    is_active = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, unique=True, index=True, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)


    password_history = relationship(
        "PasswordHistory", 
        back_populates="user", 
        cascade="all, delete-orphan",
        order_by="desc(PasswordHistory.created_at)"
    )

# --- PASSWORD HISTORY MODEL ---
class PasswordHistory(Base):
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="password_history")