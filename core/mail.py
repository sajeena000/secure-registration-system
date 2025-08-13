from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from starlette.background import BackgroundTasks

from core.config import settings

# --- EMAIL CONFIGURATION SETUP ---
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER='./frontend/templates/email' 
)

fm = FastMail(conf)

# --- FUNCTION: Send Verification Email ---
async def send_verification_email(
    email_to: EmailStr, username: str, token: str, background_tasks: BackgroundTasks
):
    """Sends an email for account verification."""
    template_body = {
        "username": username,
        "verification_link": f"http://localhost:8000/verify-email?token={token}" 
    }
    message = MessageSchema(
        subject="Verify Your CyberSecurity Account",
        recipients=[email_to],
        template_body=template_body,
        subtype="html"
    )
    
    background_tasks.add_task(fm.send_message, message, template_name="verification.html")

# --- FUNCTION: Send Password Reset Email ---
async def send_password_reset_email(
    email_to: EmailStr, username: str, token: str, background_tasks: BackgroundTasks
):
    """Sends an email for password reset."""
    template_body = {
        "username": username,
        "reset_link": f"http://localhost:8000/reset-password?token={token}" 
    }
    message = MessageSchema(
        subject="Reset Your CyberSecurity Password",
        recipients=[email_to],
        template_body=template_body,
        subtype="html"
    )
    background_tasks.add_task(fm.send_message, message, template_name="password_reset.html")