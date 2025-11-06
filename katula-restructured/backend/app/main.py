"""
Point d'entrée principal de l'application FastAPI pour l'API Katula.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

from .config import settings
from .database.connection import get_db_cursor, DatabaseConnectionError
from .utils.validators import validate_universe, validate_chip_number, get_forme_icon, get_forme_color
from .database.models import (
    FormeBase, FormeAvecFrequence, UniversFormes, 
    ChipForme, ChipDetails, UniversChips, ReponseAPI
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="API Katula",
    description="API pour l'application Katula - Gestion des formes et des univers",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des dossiers statiques
static_dir = settings.BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Gestion des erreurs globales
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return ReponseAPI.erreur(
        message="Une erreur interne est survenue",
        donnees={"detail": str(exc) if settings.DEBUG else "Internal Server Error"}
    )

@app.exception_handler(DatabaseConnectionError)
async def db_connection_error_handler(request, exc):
    logger.error(f"Erreur de connexion à la base de données: {str(exc)}")
    return ReponseAPI.erreur(
        message="Impossible de se connecter à la base de données",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )

# Route de santé
@app.get("/api/health", tags=["Système"])
async def health_check():
    """Vérifie l'état de santé de l'API."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "database": db_status
    }

# Import des routeurs
from .routes import formes, katula, ui_data

# Inclusion des routeurs
app.include_router(
    formes.router,
    prefix="/api/formes",
    tags=["Formes"]
)

app.include_router(
    katula.router,
    prefix="/api/katula",
    tags=["Katula"]
)

app.include_router(
    ui_data.router,
    prefix="/api/ui",
    tags=["Interface Utilisateur"]
)

# Route racine
@app.get("/", include_in_schema=False)
async def root():
    """Route racine de l'API."""
    return {
        "message": "Bienvenue sur l'API Katula",
        "documentation": "/api/docs",
        "version": "1.0.0"
    }

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
