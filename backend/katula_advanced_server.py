from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uvicorn
import os
from config import DB_CONFIG
from katula_complete_service import katula_service
from katula_ui_data_service import KatulaUIDataService
from katula_ui_mapper import KatulaUIMapper
from session_statistics_engine import SessionStatisticsEngine
from unified_db_session_service import UnifiedDBSessionService

app = FastAPI(title="Katula Advanced API")
ui_data_service = KatulaUIDataService(DB_CONFIG)
stats_engine = SessionStatisticsEngine(DB_CONFIG)
session_service = UnifiedDBSessionService(DB_CONFIG)

# Monter les fichiers statiques
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/", StaticFiles(directory=parent_dir, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "Katula Advanced API"}

@app.get("/api/katula/matrix/{universe}")
async def get_katula_matrix(universe: str):
    """Récupère la matrice Katula complète avec compartiments ordonnés"""
    try:
        result = katula_service.get_matrix_with_compartments(universe)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/chip/{universe}/{chip_number}")
async def get_chip_details(universe: str, chip_number: int):
    """Récupère les détails d'un chip avec compartiments ordonnés"""
    try:
        result = katula_service.get_chip_compartments(universe, chip_number)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/filters/{universe}")
async def get_filter_options(universe: str):
    """Récupère toutes les options de filtrage disponibles"""
    try:
        result = katula_service.get_filter_options(universe)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/katula/filter/{universe}")
async def apply_filters(
    universe: str,
    forme: Optional[List[str]] = Query(None),
    petique: Optional[List[str]] = Query(None),
    tome: Optional[str] = Query(None),
    granque_name: Optional[str] = Query(None),
    quadrant: Optional[str] = Query(None),
    chip_start: Optional[int] = Query(None),
    chip_end: Optional[int] = Query(None)
):
    """Applique des filtres sur la matrice Katula"""
    try:
        filters = {}
        
        if forme:
            filters['forme'] = forme
        if petique:
            filters['petique'] = petique
        if tome:
            filters['tome'] = tome
        if granque_name:
            filters['granque_name'] = granque_name
        if quadrant:
            filters['quadrant'] = quadrant
        if chip_start and chip_end:
            filters['chip_range'] = [chip_start, chip_end]
        
        result = katula_service.apply_filters(universe, filters)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/katula/forme-order/{universe}")
async def get_forme_order(universe: str):
    """Récupère l'ordre des formes pour un univers"""
    try:
        service = katula_service
        forme_order = service._get_forme_order_for_universe(universe)
        geometry = service.UNIVERSE_GEOMETRY.get(universe, {})
        
        return {
            "universe": universe,
            "forme_order": forme_order,
            "geometry": geometry,
            "total_formes": len(forme_order)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/denomination/{universe}/{denomination}")
async def get_denomination_details(universe: str, denomination: str):
    """Récupère les détails (toutes les occurrences) pour une dénomination donnée."""
    try:
        # Gérer les dénominations multiples séparées par "/"
        denominations = denomination.split('/')
        all_details = []
        for denom in denominations:
            result = katula_service.get_denomination_details(universe, denom.strip())
            if "error" in result:
                # On continue même si une dénomination échoue
                print(f"Warning: Could not fetch details for {denom}: {result['error']}")
            elif "details" in result:
                all_details.extend(result["details"])
        return {"details": all_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Serveur Katula Avancé démarré sur http://localhost:8000")
    print("Endpoints disponibles:")
    # ... (les autres prints)
    uvicorn.run(app, host="0.0.0.0", port=8000)