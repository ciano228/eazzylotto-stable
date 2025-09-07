"""
Routes pour la Table de Katula
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.katula_table_service import KatulaTableService

router = APIRouter()

@router.get("/table/{universe}")
async def get_katula_table(universe: str, db: Session = Depends(get_db)):
    """Retourne la structure de la table de Katula pour un univers"""
    return KatulaTableService.create_katula_table(universe)

@router.get("/analysis/{universe}")
async def analyze_katula_patterns(universe: str, db: Session = Depends(get_db), limit: int = 100):
    """Analyse les patterns historiques de la table de Katula"""
    return KatulaTableService.analyze_historical_patterns(db, universe, limit)

@router.get("/prediction/{universe}")
async def predict_katula_zones(universe: str, db: Session = Depends(get_db)):
    """Prédit les prochaines zones probables"""
    return KatulaTableService.predict_next_zones(db, universe)

@router.get("/combination/{combination_id}/{universe}")
async def get_katula_mapping(combination_id: int, universe: str, db: Session = Depends(get_db)):
    """Mappe une combinaison sur la table de Katula"""
    return KatulaTableService.map_combination_to_katula(db, combination_id, universe)
