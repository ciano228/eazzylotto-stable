from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.connection import get_db
from app.services.session_service import SessionService
from app.services.real_katula_service import RealKatulaService
from app.services.existing_structure_service import ExistingStructureService

router = APIRouter()

class LotteryScheduleItem(BaseModel):
    name: str
    day_offset: int  # 0=lundi, 1=mardi, etc.

class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    lottery_type: str
    numbers_per_draw: int
    total_draws: int
    lottery_schedule: Optional[List[LotteryScheduleItem]] = []
    start_date: Optional[str] = None  # Format: "DD/MM/YYYY"
    number_range_min: int = 1
    number_range_max: int = 90
    cycle_length: Optional[int] = 7  # Nombre de tirages par période

class DrawNumbersInput(BaseModel):
    numbers: List[int]
    draw_date: Optional[str] = None  # Format: "DD/MM/YYYY"
    is_no_draw: Optional[bool] = False  # Flag pour "No Draw"

@router.post("/sessions")
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle session de travail avec planning cyclique"""
    try:
        # Convertir la date de début
        start_date = datetime.strptime(session_data.start_date, "%d/%m/%Y")
        
        # Convertir le planning en format dict
        lottery_schedule = [
            {
                "name": item.name,
                "day_offset": item.day_offset
            }
            for item in session_data.lottery_schedule
        ]
        
        session = SessionService.create_work_session(
            db=db,
            name=session_data.name,
            lottery_type=session_data.lottery_type,
            numbers_per_draw=session_data.numbers_per_draw,
            total_draws=session_data.total_draws,
            lottery_schedule=lottery_schedule or [],
            start_date=start_date or datetime.now(),
            number_range_min=session_data.number_range_min,
            number_range_max=session_data.number_range_max,
            description=session_data.description,
            cycle_length=session_data.cycle_length
        )
        
        # Trigger fix_session_mapping to update session mapping
        try:
            import sys
            import os
            # Ensure backend directory is in path to import fix_session_mapping
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            if backend_dir not in sys.path:
                sys.path.append(backend_dir)
            
            from fix_session_mapping import fix_session_mapping
            print("Triggering fix_session_mapping after session creation...")
            fix_session_mapping()
        except Exception as e:
            print(f"Warning: Failed to run fix_session_mapping: {e}")
        
        return {
            "message": "Session créée avec succès",
            "id": session.id,
            "name": session.name,
            "description": session.description,
            "lottery_type": session.lottery_type,
            "numbers_per_draw": session.numbers_per_draw,
            "total_draws": session.total_draws,
            "cycle_length": session.cycle_length,
            "is_active": session.is_active,
            "created_at": session.created_at.strftime("%d/%m/%Y %H:%M")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_all_sessions(db: Session = Depends(get_db)):
    """Récupérer toutes les sessions disponibles"""
    try:
        # Fallback sur les données locales
        sessions = SessionService.get_all_sessions(db)
        
        sessions_data = []
        for session in sessions:
            progress = SessionService.get_session_progress(db, session.id)
            sessions_data.append({
                "id": session.id,
                "name": session.name,
                "description": session.description,
                "lottery_type": session.lottery_type,
                "numbers_per_draw": session.numbers_per_draw,
                "number_range_min": session.number_range_min,
                "number_range_max": session.number_range_max,
                "total_draws": session.total_draws,
                "current_draw": session.current_draw,
                "cycle_length": session.cycle_length,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "status": "active" if session.is_active else "inactive",
                "universe": session.lottery_type,  # Pour compatibilité frontend
                "start_date": session.start_date.isoformat() if session.start_date else None,
                "end_date": progress.get("end_date"),
                "progress": progress
            })
        
        return {
            "value": sessions_data,
            "total": len(sessions_data),
            "data_source": "local_database"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des sessions: {str(e)}")

@router.get("/sessions/active")
async def get_active_session(db: Session = Depends(get_db)):
    """Récupérer la session active"""
    try:
        session = SessionService.get_active_session(db)
        
        if not session:
            return {"message": "Aucune session active"}
        
        progress = SessionService.get_session_progress(db, session.id)
        
        return {
            "session": {
                "id": session.id,
                "name": session.name,
                "description": session.description,
                "lottery_type": session.lottery_type,
                "numbers_per_draw": session.numbers_per_draw,
                "number_range_min": session.number_range_min,
                "number_range_max": session.number_range_max,
                "total_draws": session.total_draws,
                "current_draw": session.current_draw,
                "cycle_length": session.cycle_length,
                "is_active": session.is_active
            },
            "progress": progress
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/activate")
async def activate_session(session_id: int, db: Session = Depends(get_db)):
    """Activer une session spécifique et synchroniser automatiquement les tirages"""
    try:
        session = SessionService.activate_session(db, session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        # Auto-synchronisation intelligente des tirages avec le planning
        sync_result = SessionService.sync_session_schedule(db, session_id)
        
        return {
            "message": f"Session '{session.name}' activée et synchronisée",
            "session_id": session.id,
            "sync_info": {
                "created_draws": sync_result.get("created", 0),
                "updated_draws": sync_result.get("updated", 0),
                "total_draws": sync_result.get("total", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/current-draw")
async def get_current_draw(session_id: int, db: Session = Depends(get_db)):
    """Récupérer le tirage actuel d'une session"""
    try:
        draw = SessionService.get_current_draw(db, session_id)
        
        if not draw:
            raise HTTPException(status_code=404, detail="Tirage actuel non trouvé")
        
        return {
            "draw_id": draw.id,
            "draw_number": draw.draw_number,
            "lottery_name": draw.lottery_name,
            "winning_numbers": draw.winning_numbers,
            "is_completed": draw.is_completed,
            "draw_date": draw.draw_date.strftime("%d/%m/%Y")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/draws/{draw_number}")
async def save_draw_numbers(
    session_id: int, 
    draw_number: int, 
    numbers_data: DrawNumbersInput, 
    db: Session = Depends(get_db)
):
    """Sauvegarder les numéros d'un tirage"""
    try:
        # Validation des numéros (sauf si c'est un "No Draw")
        if not numbers_data.is_no_draw:
            if len(numbers_data.numbers) == 0:
                raise HTTPException(status_code=400, detail="Au moins un numéro est requis")
            # Vérifier les doublons
            if len(numbers_data.numbers) != len(set(numbers_data.numbers)):
                raise HTTPException(status_code=400, detail="Les numéros ne peuvent pas être dupliqués")
        # Convertir la date si fournie
        draw_date = None
        if numbers_data.draw_date:
            draw_date = datetime.strptime(numbers_data.draw_date, "%d/%m/%Y")
        # Pour "No Draw", passer une liste vide
        numbers_to_save = [] if numbers_data.is_no_draw else numbers_data.numbers
        draw = SessionService.save_draw_numbers(
            db=db,
            session_id=session_id,
            draw_number=draw_number,
            numbers=numbers_to_save,
            draw_date=draw_date,
            is_no_draw=numbers_data.is_no_draw
        )
        message = "No Draw sauvegardé avec succès" if numbers_data.is_no_draw else "Numéros sauvegardés avec succès"
        return {
            "message": message,
            "draw_id": draw.id,
            "draw_number": draw.draw_number,
            "numbers": draw.winning_numbers,
            "is_no_draw": draw.is_no_draw
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/progress")
async def get_session_progress(session_id: int, db: Session = Depends(get_db)):
    """Obtenir le progrès d'une session"""
    try:
        progress = SessionService.get_session_progress(db, session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return progress
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/sync")
async def sync_session_schedule(session_id: int, db: Session = Depends(get_db)):
    """Synchronize session draws with expected schedule, creating missing placeholders"""
    try:
        result = SessionService.sync_session_schedule(db, session_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/draws")
async def get_session_draws(session_id: int, source: Optional[str] = None, db: Session = Depends(get_db)):
    """Récupérer tous les tirages d'une session, en spécifiant la source de données."""
    try:
        if source == "real":
            # Utiliser le service qui comble les tirages manquants
            result = ExistingStructureService.get_real_session_draws(session_id)
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            return result["value"]

        # Comportement par défaut pour la base de données locale
        draws = SessionService.get_session_draws(db, session_id)
        
        return [
            {
                "id": draw.id,
                "draw_number": draw.draw_number,
                "lottery_name": draw.lottery_name,
                "draw_date": draw.draw_date.strftime("%d/%m/%Y"),
                "winning_numbers": draw.winning_numbers or [],
                "is_completed": draw.is_completed,
                "is_no_draw": getattr(draw, "is_no_draw", False)
            }
            for draw in draws
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}/draws/{draw_id}")
async def update_draw_numbers(
    session_id: int,
    draw_id: int,
    numbers_data: DrawNumbersInput,
    db: Session = Depends(get_db)
):
    """Modifier les numéros d'un tirage existant"""
    try:
        from app.models.session import SessionDraw
        
        # Trouver le tirage à modifier
        draw = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id,
            SessionDraw.id == draw_id
        ).first()
        
        if not draw:
            raise HTTPException(status_code=404, detail="Tirage non trouvé")
        
        # Mettre à jour les numéros
        draw.winning_numbers = numbers_data.numbers
        draw.is_completed = True
        
        # Mettre à jour la date si fournie
        if numbers_data.draw_date:
            draw.draw_date = datetime.strptime(numbers_data.draw_date, "%d/%m/%Y")
        
        db.commit()
        db.refresh(draw)
        
        return {
            "message": "Tirage modifié avec succès",
            "draw_id": draw.id,
            "draw_number": draw.draw_number,
            "numbers": draw.winning_numbers
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}/draws/{draw_id}")
async def delete_draw(
    session_id: int,
    draw_id: int,
    db: Session = Depends(get_db)
):
    """Supprimer un tirage d'une session"""
    try:
        from app.models.session import SessionDraw, WorkSession
        
        # Vérifier que la session existe
        session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        # Trouver le tirage
        draw = db.query(SessionDraw).filter(
            SessionDraw.session_id == session_id,
            SessionDraw.id == draw_id
        ).first()
        
        if not draw:
            raise HTTPException(status_code=404, detail="Tirage non trouvé")
        
        # Sauvegarder le numéro de tirage pour le message
        draw_number = draw.draw_number
        
        # Supprimer le tirage
        db.delete(draw)
        db.commit()
        
        return {"message": f"Tirage {draw_number} supprimé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")