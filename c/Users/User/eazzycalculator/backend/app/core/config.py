from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EazzyCalculator"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://eazzycalculator.com",
    ]
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Katulaa_33@localhost:5432/katooling_main_system"
    )
    
    # API Security
    API_KEY_NAME: str = "access_token"
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Instance de configuration globale
settings = Settings()
