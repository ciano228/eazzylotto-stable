"""
Version finale de l'API FastAPI pour EazzyCalculator
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.database.connection import Base, engine

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour la gestion des erreurs
@app.middleware("http")
async def error_handling(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Une erreur interne s'est produite"}
        )

# Initialisation de la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage de l'API...")
    try:
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur d'initialisation de la base de données: {str(e)}")

# Routes de base
@app.get("/")
async def root():
    """Route racine pour vérifier que l'API fonctionne"""
    return {
        "message": "EazzyCalculator API is running",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {
        "status": "healthy",
        "message": "API is running",
        "environment": os.getenv("ENV", "development")
    }

# Import et montage des routes
from app.routes import api_router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
