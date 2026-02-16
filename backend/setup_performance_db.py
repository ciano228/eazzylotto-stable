import sys
import os
# Add the current directory to sys.path to handle imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, Base
from app.models.performance import PredictionRecord

def setup_db():
    print("🚀 Initialisation de la table des performances...")
    try:
        # This will create all tables defined in models that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("✅ Table 'prediction_records' créée avec succès dans PostgreSQL.")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table : {e}")

if __name__ == "__main__":
    setup_db()
