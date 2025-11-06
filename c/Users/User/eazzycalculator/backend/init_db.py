from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Katulaa_33")
POSTGRES_DB = os.getenv("POSTGRES_DB", "katooling_main_system")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Définition de la table combinations
combinations = Table(
    "combinations",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("universe", String, index=True),
    Column("data", JSONB),  # Utilisation de JSONB pour PostgreSQL
    Column("tome", String),
    Column("granque", String),
    Column("petique", String),
)

def init_db():
    print("Création des tables...")
    metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init_db()