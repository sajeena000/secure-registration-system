# Secure Registration System 

This project is a prototype secure user registration system.
The application is built using Python and the FastAPI framework. It demonstrates the practical application of key cybersecurity principles in a web application context, focusing on secure user onboarding processes.

# Features
- User-Friendly Registration UI: A clean, simple web interface for users to create an account.
- Robust Password Strength Analysis: Algorithmically determines the strength of a user's chosen password based on a set of configurable criteria (length, character types).
- Instant User Feedback: Provides clear, immediate feedback to the user on their password's strength and what is required to improve it.
- Image CAPTCHA Verification: Implements a self-hosted image CAPTCHA to distinguish between human users and automated bots, a critical defense against credential stuffing and spam account creation.
- Secure Password Storage: Uses the industry-standard bcrypt algorithm to hash and salt user passwords before storage, ensuring that plain-text passwords are never stored.
- Clear Success and Error Messaging: Guides the user through the registration process with informative messages.

# Technology Stack
- **Backend**: Python 3.9+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Templating**: Jinja2
- **Key Libraries**:
  - `bcrypt` – Secure password hashing with adaptive complexity
  - `Pillow` – Image processing for CAPTCHA generation
  - `jinja2` – HTML template rendering with auto-escaping
  - `sqlalchemy` – Database ORM with SQL injection protection

# Project Structure
The project is organized as follows to maintain a clean separation of concerns:

```
/SAJEENAMALLA_CYBERSECURITY
├── api/
│   └── v1/               # Contains all API v1 endpoints (e.g., for users, auth).
├── core/
│   ├── config.py         # Manages application settings and environment variables.
│   └── security.py       # Handles all security logic (password hashing, JWTs).
├── db/
│   ├── base.py           # Database engine and session setup.
│   └── models.py         # SQLAlchemy database models (e.g., User table).
├── frontend/
│   ├── static/           # Static assets (CSS, JavaScript, Images).
│   └── templates/        # Jinja2 HTML templates for the user interface.
├── schemas/
│   ├── user.py           # Pydantic schemas for user data validation.
│   └── captcha.py        # Pydantic schemas for CAPTCHA request/response.
├── .env                  # Stores environment variables and secrets (not committed).
├── main.py               # The main entry point for the FastAPI application.
├── requirements.txt      # A list of all Python dependencies for the project.
└── README.md             # This file, explaining the project.
```

# Setup and Installation
To run this project locally, please follow these steps.

### Prerequisites
1. Python 3.8 or newer.
2. pip (Python package installer).
3. Git (for cloning the repository)

### Installation Steps:

**Step 1: Clone the Repository**  
If you downloaded the ZIP manually, extract it to your working directory.

If you're using Git:
```bash
git clone https://github.com/sajeena000/secure-registration-system.git
cd SAJEENAMALLA_CYBERSECURITY
```

**Step 2: Navigate to the Project Directory**  
Open a terminal or command prompt and change to the project's root directory.
```bash
cd path/to/SAJEENAMALLA_CYBERSECURITY
```

**Step 3: Create and Activate a Virtual Environment (Recommended)**  
This isolates the project's dependencies from your system's global Python environment.

- On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

- On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Step 4: Configure Environment Variables (CRITICAL)**  
The application requires an .env file for configuration. A template named .env.example is provided.
- Copy the template to create your local configuration file.
On macOS/Linux: cp .env.example .env
On Windows: copy .env.example .env
- Edit the .env file and provide your own values. This file stores sensitive information and should never be committed to version control.
```ini
# --- Security Settings ---
# Generate a new strong key with: openssl rand -hex 32
SECRET_KEY="PASTE_YOUR_OWN_STRONG_RANDOM_SECRET_KEY_HERE"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# --- Password Policy ---
# Defines rules for password security
PASSWORD_LIFESPAN_DAYS=90
PASSWORD_HISTORY_LIMIT=3

# --- Email Configuration ---
# Use your actual email provider's details or a service like Mailtrap for development.
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_FROM_NAME="CyberSecurity System"
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true
VALIDATE_CERTS=true
```

**Step 5: Install Dependencies**  
Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

- Sample `requirements.txt`:
```
fastapi
uvicorn[standard]
sqlalchemy
jinja2
bcrypt
pillow
python-dotenv
python-multipart
```

**Step 6: Run the Application**  
Once the setup is complete, you can start the web server with the following command:

```bash
uvicorn main:app --reload
```

1. `uvicorn`: The ASGI server that runs the application.
2. `main:app`: Tells Uvicorn to find the `app` object inside the `main.py` file.
3. `--reload`: Enables auto-reload, so the server restarts automatically when you make code changes.

After running the command, you will see output similar to this:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open your web browser and navigate to `http://127.0.0.1:8000` to use the application.

