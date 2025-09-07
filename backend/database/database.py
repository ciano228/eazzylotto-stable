from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eazzylotto.db")

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialiser la base de données
def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée")