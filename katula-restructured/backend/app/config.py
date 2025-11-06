import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Settings(BaseSettings):    
    # Configuration de la base de données
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "katooling_main_system")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Configuration du serveur
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Configuration JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "votre_clé_secrète_par_défaut")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuration des univers
    VALID_UNIVERSES: list[str] = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    # Chemins
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # Configuration CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Instance des paramètres
settings = Settings()

# Configuration de la base de données au format dictionnaire pour SQLAlchemy
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
