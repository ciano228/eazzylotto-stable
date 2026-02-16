"""
Serveur de Test pour l'Affichage Table de Katula
Serveur FastAPI pour tester le service d'affichage avec icônes et dénominations
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database.database_postgresql import get_db
from backend.app.routes.katula_display_routes import router as katula_display_router

app = FastAPI(
    title="EazzyCalculator - Affichage Table de Katula",
    description="API pour l'affichage formaté de la table de Katula avec icônes et dénominations",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(katula_display_router)

@app.get("/")
async def root():
    """Page d'accueil de l'API d'affichage"""
    return {
        "message": "EazzyCalculator - Affichage Table de Katula",
        "version": "1.0.0",
        "description": "Service d'affichage formaté avec icônes et dénominations",
        "endpoints": {
            "health": "/api/katula-display/health",
            "table_formatted": "/api/katula-display/{universe}",
            "chip_display": "/api/katula-display/{universe}/chip/{chip_number}",
            "html_table": "/api/katula-display/{universe}/html",
            "simple_matrix": "/api/katula-display/{universe}/matrix-simple",
            "icons_list": "/api/katula-display/icons/list"
        },
        "universes": ["mundo", "roaster", "trigga", "sunshine", "fruity"],
        "features": [
            "Chips nommés (chip1, chip2, ...)",
            "Tiroirs avec icônes par forme",
            "Dénominations séparées par '/'",
            "Données PostgreSQL réelles",
            "HTML complet généré"
        ],
        "examples": {
            "mundo_table": "/api/katula-display/mundo",
            "chip1_mundo": "/api/katula-display/mundo/chip/1",
            "html_fruity": "/api/katula-display/fruity/html"
        },
        "documentation": "/docs"
    }

@app.get("/api/health")
async def api_health():
    """Vérification de santé de l'API d'affichage"""
    return {
        "status": "healthy",
        "service": "katula-display-api",
        "database": "postgresql",
        "version": "1.0.0"
    }

@app.get("/api/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test de connexion à la base de données"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test"))
        test_result = result.fetchone()
        
        return {
            "database_status": "connected",
            "test_query": "SELECT 1",
            "result": test_result.test if test_result else None
        }
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e)
        }

@app.get("/demo/{universe}")
async def demo_table(universe: str):
    """Page de démonstration rapide"""
    return {
        "demo": f"Table de Katula - {universe.upper()}",
        "description": "Démonstration de l'affichage formaté",
        "links": {
            "html_complet": f"/api/katula-display/{universe}/html",
            "donnees_json": f"/api/katula-display/{universe}",
            "matrice_simple": f"/api/katula-display/{universe}/matrix-simple"
        },
        "exemple_chip": {
            "chip1": f"/api/katula-display/{universe}/chip/1",
            "chip24": f"/api/katula-display/{universe}/chip/24",
            "chip48": f"/api/katula-display/{universe}/chip/48"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Demarrage du serveur d'affichage Table de Katula...")
    print("API: http://localhost:8005/")
    print("Health: http://localhost:8005/api/health")
    print("Demo Mundo: http://localhost:8005/demo/mundo")
    print("HTML Mundo: http://localhost:8005/api/katula-display/mundo/html")
    print("Documentation: http://localhost:8005/docs")
    
    uvicorn.run(
        "katula_display_server:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )