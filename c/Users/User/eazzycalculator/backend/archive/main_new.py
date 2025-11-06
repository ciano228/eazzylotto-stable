"""
Point d'entrée principal de l'API FastAPI pour EazzyCalculator
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database.connection import Base, engine

# Charger les variables d'environnement
load_dotenv()

# Créer le répertoire data s'il n'existe pas
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API pour l'analyse et la prédiction des numéros de loterie",
    version="2.0.0"
)

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API pour l'analyse et la prédiction des numéros de loterie",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Créer les tables de la base de données
print("[INFO] Initialisation de la base de données...")
try:
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables créées avec succès")
except Exception as e:
    print(f"[ERROR] Erreur création des tables: {e}")

# Routes de base
@app.get("/")
async def root():
    """Route racine pour vérifier que l'API fonctionne"""
    return {
        "message": "EazzyCalculator API is running",
        "version": "2.0.0",
        "status": "healthy",
        "routes": [
            {"path": "/", "method": "GET", "description": "Cette page"},
            {"path": "/health", "method": "GET", "description": "Vérification de santé"},
            {"path": "/api/test/test", "method": "GET", "description": "Route de test"},
            {"path": "/api/katula/table/{universe}", "method": "GET", "description": "Structure de la table Katula"}
        ]
    }

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    try:
        # Vérifier la connexion à la base de données
        Base.metadata.create_all(bind=engine)
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "message": "API is running",
        "database": db_status,
        "environment": os.getenv("ENV", "development")
    }

# Monter les routes dynamiquement
print("[INFO] Montage des routes...")
try:
    from app.routes import api_router
    app.include_router(api_router, prefix="/api")
    print("[OK] Router principal monté")
except Exception as e:
    print(f"[ERROR] Erreur montage router principal: {e}")
    
# Configuration terminée
print("[INFO] Configuration de l'API terminée")

if __name__ == "__main__":
    import uvicorn
    
    # Port par défaut 8000, mais peut être modifié par variable d'environnement
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
