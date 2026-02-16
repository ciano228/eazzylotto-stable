"""
Serveur pour la Vraie Table de Katula
Utilise la table 'combinations' avec la logique métier originale
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database.database_postgresql import get_db
from backend.app.routes.katula_combinations_routes import router as katula_real_router

app = FastAPI(
    title="EazzyCalculator - Vraie Table de Katula",
    description="API pour la vraie table de Katula basée sur la table 'combinations'",
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
app.include_router(katula_real_router)

@app.get("/")
async def root():
    """Page d'accueil de l'API vraie table de Katula"""
    return {
        "message": "EazzyCalculator - Vraie Table de Katula",
        "version": "1.0.0",
        "description": "Service basé sur la table 'combinations' avec la logique métier originale",
        "data_source": "combinations_table (PostgreSQL)",
        "endpoints": {
            "health": "/api/katula-real/health",
            "table": "/api/katula-real/{universe}",
            "chip": "/api/katula-real/{universe}/chip/{chip_number}",
            "denomination": "/api/katula-real/{universe}/denomination/{denomination}",
            "html": "/api/katula-real/{universe}/html",
            "summary": "/api/katula-real/{universe}/summary"
        },
        "universes": ["mundo", "roaster", "trigga", "sunshine", "fruity"],
        "logique_metier": {
            "structure": "Matrice 8x6 = 48 chips",
            "tiroirs": "4 tiroirs par chip selon l'ordre des formes",
            "denominations": "Séparées par '/' si multiples",
            "icones": "Une icône par forme (⬜🔺🔵▬)",
            "source_donnees": "Table 'combinations' PostgreSQL"
        },
        "exemples": {
            "table_mundo": "/api/katula-real/mundo",
            "chip1_mundo": "/api/katula-real/mundo/chip/1",
            "denomination": "/api/katula-real/mundo/denomination/table 2",
            "html_mundo": "/api/katula-real/mundo/html",
            "summary_mundo": "/api/katula-real/mundo/summary"
        },
        "documentation": "/docs"
    }

@app.get("/api/health")
async def api_health():
    """Vérification de santé de l'API vraie table"""
    return {
        "status": "healthy",
        "service": "katula-real-api",
        "database": "postgresql",
        "table_source": "combinations",
        "version": "1.0.0"
    }

@app.get("/api/test-combinations")
async def test_combinations_table(db: Session = Depends(get_db)):
    """Test de la table combinations"""
    try:
        from sqlalchemy import text
        
        # Test de base
        result = db.execute(text("SELECT COUNT(*) as total FROM combinations"))
        total = result.fetchone().total
        
        # Test par univers
        result = db.execute(text("""
            SELECT univers, COUNT(*) as count 
            FROM combinations 
            WHERE univers IS NOT NULL 
            GROUP BY univers 
            ORDER BY univers
        """))
        by_universe = {row.univers: row.count for row in result.fetchall()}
        
        # Test des colonnes importantes
        result = db.execute(text("""
            SELECT 
                COUNT(DISTINCT chip) as chips,
                COUNT(DISTINCT forme) as formes,
                COUNT(DISTINCT denomination) as denominations
            FROM combinations 
            WHERE chip IS NOT NULL AND forme IS NOT NULL
        """))
        stats = result.fetchone()
        
        return {
            "database_status": "connected",
            "table": "combinations",
            "total_rows": total,
            "by_universe": by_universe,
            "statistics": {
                "unique_chips": stats.chips,
                "unique_formes": stats.formes,
                "unique_denominations": stats.denominations
            }
        }
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e)
        }

@app.get("/demo/{universe}")
async def demo_real_table(universe: str):
    """Démonstration de la vraie table de Katula"""
    return {
        "demo": f"Vraie Table de Katula - {universe.upper()}",
        "description": "Basée sur la table 'combinations' avec la logique métier originale",
        "structure": {
            "matrice": "8 lignes x 6 colonnes = 48 chips",
            "tiroirs": "4 tiroirs par chip (carre, triangle, cercle, rectangle)",
            "denominations": "Groupées par forme avec séparateur '/'",
            "icones": "⬜ Carré, 🔺 Triangle, 🔵 Cercle, ▬ Rectangle"
        },
        "liens": {
            "table_complete": f"/api/katula-real/{universe}",
            "html_visuel": f"/api/katula-real/{universe}/html",
            "resume": f"/api/katula-real/{universe}/summary"
        },
        "exemples_chips": {
            "chip1": f"/api/katula-real/{universe}/chip/1",
            "chip24": f"/api/katula-real/{universe}/chip/24",
            "chip48": f"/api/katula-real/{universe}/chip/48"
        },
        "exemple_denomination": f"/api/katula-real/{universe}/denomination/table 2"
    }

if __name__ == "__main__":
    import uvicorn
    print("Demarrage du serveur Vraie Table de Katula...")
    print("API: http://localhost:8006/")
    print("Health: http://localhost:8006/api/health")
    print("Test Combinations: http://localhost:8006/api/test-combinations")
    print("Demo Mundo: http://localhost:8006/demo/mundo")
    print("HTML Mundo: http://localhost:8006/api/katula-real/mundo/html")
    print("Documentation: http://localhost:8006/docs")
    
    uvicorn.run(
        "katula_real_server:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )