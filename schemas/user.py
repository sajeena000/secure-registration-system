from typing import Optional
from pydantic import BaseModel, Field, EmailStr, model_validator

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreate':
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

class UserCreateWithCaptcha(UserCreate):
    captcha_id: str
    captcha_text: str

class User(UserBase):
    id: int
    is_active: bool 

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class EmailSchema(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'PasswordReset':
        if self.new_password != self.confirm_new_password:
            raise ValueError('Passwords do not match')
        return self