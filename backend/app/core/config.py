from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EazzyCalculator"
    
    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://eazzycalculator.com",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
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
    
    # Missing fields from .env
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_VERSION: str = "2.0.0"
    API_TITLE: str = "EazzyCalculator API"
    LOG_LEVEL: str = "INFO"
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 8000

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )

# Instance de configuration globale
settings = Settings()
