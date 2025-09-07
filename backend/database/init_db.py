"""
Initialisation et gestion de la base de données de production
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import engine, Base
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def init_db():
    """Initialise la base de données avec toutes les tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès")
        
        # Créer les index pour les performances
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_katula_universe 
                ON katula_tables (universe);
                
                CREATE INDEX IF NOT EXISTS idx_katula_created_at 
                ON katula_tables (created_at);
            """))
        logger.info("Index créés avec succès")
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur d'initialisation de la base de données: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Démarrage de l'initialisation de la base de données...")
        init_db()
        logger.info("Base de données initialisée avec succès!")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)
