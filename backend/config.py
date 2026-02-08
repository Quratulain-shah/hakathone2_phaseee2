"""
Configuration settings for the Todo App backend API
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")

class Settings:
    """Application settings loaded from environment variables"""

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./todo_app.db")

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("AUTH_SECRET", "KPUqFcCE/cmK7jg73LieWXczeHwnHlb4Hde1EcVrbCo="))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # App settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Todo App Backend API"

    # For mock authentication in Phase 2
    MOCK_USER_ID: int = 1  # Default mock user ID


settings = Settings()