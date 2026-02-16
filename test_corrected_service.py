"""
Test du Service Katula Corrigé
Vérifie que le service utilise maintenant la table 'combinations'
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os

# Ajouter le chemin backend au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database.database_postgresql import get_db

app = FastAPI(
    title="Test Service Katula Corrigé",
    description="Test du service Katula utilisant la table 'combinations'",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Test Service Katula Corrigé",
        "description": "Vérifie que le service utilise la table 'combinations'",
        "endpoints": {
            "test_service": "/test-service/{universe}",
            "test_chip": "/test-chip/{universe}/{chip_number}",
            "test_db": "/test-db"
        }
    }

@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test de la connexion et de la table combinations"""
    try:
        from sqlalchemy import text
        
        # Test table combinations
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
        
        return {
            "database_status": "connected",
            "table": "combinations",
            "total_rows": total,
            "by_universe": by_universe
        }
    except Exception as e:
        return {"database_status": "error", "error": str(e)}

@app.get("/test-service/{universe}")
async def test_corrected_service(universe: str):
    """Test du service Katula corrigé"""
    try:
        # Import du service corrigé
        from backend.katula_complete_service import KatulaCompleteService
        
        service = KatulaCompleteService()
        result = service.get_katula_table(universe)
        
        return {
            "success": True,
            "universe": universe,
            "service_result": result,
            "uses_combinations_table": result.get('source') == 'combinations'
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test-chip/{universe}/{chip_number}")
async def test_chip_data(universe: str, chip_number: int):
    """Test des données d'un chip spécifique"""
    try:
        from backend.katula_complete_service import KatulaCompleteService
        
        service = KatulaCompleteService()
        result = service.get_chip_compartments(universe, chip_number)
        
        return {
            "success": True,
            "universe": universe,
            "chip_number": chip_number,
            "chip_data": result
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Demarrage du test du service Katula corrige...")
    print("API: http://localhost:8007/")
    print("Test DB: http://localhost:8007/test-db")
    print("Test Service Mundo: http://localhost:8007/test-service/mundo")
    print("Test Chip1 Mundo: http://localhost:8007/test-chip/mundo/1")
    
    uvicorn.run(
        "test_corrected_service:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )