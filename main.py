from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import auth, captcha, users
from api.deps import redirect_if_authenticated, get_current_user_or_redirect
from db.base import create_db_and_tables
from db.models import User

create_db_and_tables()

# Initialize the FastAPI application with metadata
app = FastAPI(
    title="Advanced CyberSecurity System",
    description="CET324 Assignment 2 - University of Sunderland",
    version="1.0.0"
)

# Define allowed origins for CORS (e.g., frontend dev servers)
origins = [
    "http://localhost",
    "http://localhost:8080",
]

# Configure middleware to enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


# --- API ROUTERS ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(captcha.router, prefix="/api/v1/captcha", tags=["CAPTCHA"])


# --- FRONTEND ROUTES ---
@app.get("/", response_class=HTMLResponse, tags=["Frontend"], dependencies=[Depends(redirect_if_authenticated)])
async def serve_login_page(request: Request):
    """
    Serves the login page.
    Redirects to /profile if the user is already authenticated.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["Frontend"], dependencies=[Depends(redirect_if_authenticated)])
async def serve_register_page(request: Request):
    """
    Serves the registration page.
    Redirects to /profile if the user is already authenticated.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse, tags=["Frontend"])
async def serve_profile_page(request: Request,current_user: User = Depends(get_current_user_or_redirect)):
    """
    Serves the user profile page.
    This route is protected; it will redirect to login if not authenticated.
    """
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/verify-email", response_class=HTMLResponse, tags=["Frontend"])
async def serve_verify_email_page(request: Request, token: str):
    """Serves the page to handle email verification."""
    return templates.TemplateResponse("verify_email.html", {"request": request, "token": token})

@app.get("/forgot-password", response_class=HTMLResponse, tags=["Frontend"])
async def serve_forgot_password_page(request: Request):
    """Serves the forgot password page."""
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse, tags=["Frontend"])
async def serve_reset_password_page(request: Request, token: str):
    """Serves the page to reset the password, using the token from the URL."""
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@app.get("/unauthorized", response_class=HTMLResponse, tags=["Frontend"])
async def serve_unauthorized_page(request: Request):
    """Serves the unauthorized access page."""
    return templates.TemplateResponse("unauthorized.html", {"request": request})

# --- EXCEPTION HANDLERS ---
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Serves the custom 404 page for any 'Not Found' error.
    """
    return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)