from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.connection import get_db
from app.services.analysis_service import AnalysisService
from app.models.session import WorkSession

router = APIRouter()

@router.get("/draw/{draw_id}")
async def analyze_draw(
    draw_id: int, 
    universe: Optional[str] = Query(None, description="Univers spécifique à analyser"),
    db: Session = Depends(get_db)
):
    """Analyser un tirage spécifique"""
    try:
        result = AnalysisService.analyze_draw(db, draw_id, universe)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journal")
async def get_statistical_journal(
    universe: Optional[str] = Query("mundo", description="Filtrer par univers (défaut: mundo)"),
    start_date: Optional[str] = Query(None, description="Date de début (DD/MM/YYYY)"),
    end_date: Optional[str] = Query(None, description="Date de fin (DD/MM/YYYY)"),
    period_start: Optional[int] = Query(None, description="Période de début"),
    period_end: Optional[int] = Query(None, description="Période de fin"),
    periodicity: int = Query(1, description="Nombre de tirages par période"),
    session_id: Optional[int] = Query(None, description="ID de la session cyclique"),
    db: Session = Depends(get_db)
):
    """Générer le journal statistique avec périodicité et filtres avancés"""
    try:
        result = AnalysisService.generate_statistical_journal(
            db=db,
            universe=universe,
            start_date=start_date,
            end_date=end_date,
            period_start=period_start,
            period_end=period_end,
            periodicity=periodicity,
            session_id=session_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frequencies")
async def get_frequencies(
    universe: Optional[str] = Query(None, description="Filtrer par univers"),
    limit: int = Query(100, description="Nombre de tirages à analyser"),
    db: Session = Depends(get_db)
):
    """Obtenir les fréquences d'apparition des attributs"""
    try:
        journal = AnalysisService.generate_statistical_journal(db, universe, limit)
        frequencies = AnalysisService.calculate_frequencies(journal)
        
        return {
            "frequencies": frequencies,
            "analyzed_entries": len(journal),
            "universe_filter": universe
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/universes")
async def get_universes():
    """Obtenir la liste des univers disponibles"""
    return {
        "universes": [
            {"id": "mundo", "name": "Mundo"},
            {"id": "fruity", "name": "Fruity"},
            {"id": "trigga", "name": "Trigga"},
            {"id": "roaster", "name": "Roaster"},
            {"id": "sunshine", "name": "Sunshine"}
        ]
    }

@router.get("/session/{session_id}")
async def analyze_session(
    session_id: int,
    universe: Optional[str] = Query("mundo", description="Univers à analyser"),
    periodicity: int = Query(3, description="Périodicité pour l'analyse"),
    db: Session = Depends(get_db)
):
    """Analyser une session cyclique complète"""
    try:
        from app.services.session_service import SessionService
        
        # Vérifier que la session existe
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        # Obtenir les tirages complétés de la session
        session_draws = SessionService.get_session_draws(db, session_id)
        completed_draws = [draw for draw in session_draws if draw.is_completed]
        
        if not completed_draws:
            return {
                "session_info": {
                    "id": session.id,
                    "name": session.name,
                    "lottery_type": session.lottery_type
                },
                "message": "Aucun tirage complété dans cette session",
                "total_draws": len(session_draws),
                "completed_draws": 0
            }
        
        # Générer le journal statistique pour cette session
        result = AnalysisService.generate_statistical_journal(
            db=db,
            universe=universe,
            periodicity=periodicity,
            session_id=session_id
        )
        
        # Ajouter les informations de session
        result["session_info"] = {
            "id": session.id,
            "name": session.name,
            "lottery_type": session.lottery_type,
            "cycle_length": session.cycle_length,
            "total_draws": session.total_draws,
            "completed_draws": len(completed_draws)
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/combinations/{num1}/{num2}")
async def get_combination_info(num1: int, num2: int, db: Session = Depends(get_db)):
    """Obtenir les informations d'une combinaison spécifique"""
    try:
        from app.services.combination_service import CombinationService
        
        combo_info = CombinationService.get_combination_info(db, num1, num2)
        
        if not combo_info:
            raise HTTPException(
                status_code=404, 
                detail=f"Combinaison {num1}-{num2} non trouvée dans la base de données"
            )
        
        return combo_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))