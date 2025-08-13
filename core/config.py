from pydantic import EmailStr, BaseModel 
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    PASSWORD_LIFESPAN_DAYS: int = 90
    PASSWORD_HISTORY_LIMIT: int = 3 

    # Mail Settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    class Config:
        env_file = ".env"

settings = Settings()