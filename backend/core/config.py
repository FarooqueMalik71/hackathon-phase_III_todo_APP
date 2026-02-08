import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./todo_app.db"
    )

    # Better Auth configuration
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "")
    BETTER_AUTH_URL: str = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Hackathon Todo Backend"

    # Security
    ALLOWED_HOSTS: List[str] = ["*"]

    class Config:
        case_sensitive = True


settings = Settings()
