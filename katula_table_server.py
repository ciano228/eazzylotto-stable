"""
Serveur de Test pour la Table de Katula Intégrée
Serveur FastAPI pour tester les nouveaux services de table Katula
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database.database_postgresql import get_db
from backend.app.routes.katula_table_routes import router as katula_table_router

app = FastAPI(
    title="EazzyCalculator - Table de Katula API",
    description="API pour la table de Katula avec données PostgreSQL réelles",
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
app.include_router(katula_table_router)

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "EazzyCalculator - Table de Katula API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/katula-table/health",
            "table": "/api/katula-table/{universe}",
            "chip": "/api/katula-table/{universe}/chip/{chip_number}",
            "analysis": "/api/katula-table/{universe}/analysis",
            "matrix": "/api/katula-table/{universe}/matrix",
            "zones": "/api/katula-table/{universe}/zones",
            "neighbors": "/api/katula-table/utils/neighbors/{chip_number}",
            "distance": "/api/katula-table/utils/distance/{chip1}/{chip2}"
        },
        "universes": ["mundo", "roaster", "trigga", "sunshine", "fruity"],
        "documentation": "/docs"
    }

@app.get("/api/health")
async def api_health():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "service": "katula-table-api",
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur Table de Katula...")
    print("📊 API Documentation: http://localhost:8003/docs")
    print("🔍 Health Check: http://localhost:8003/api/health")
    print("🎯 Test Database: http://localhost:8003/api/test-db")
    print("📋 Endpoints: http://localhost:8003/")
    
    uvicorn.run(
        "katula_table_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )