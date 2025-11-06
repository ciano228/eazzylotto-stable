from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.draw import Draw
from app.services.combination_service import CombinationService

router = APIRouter()

class DrawCreate(BaseModel):
    lottery_name: str
    draw_date: str  # Format: "DD/MM/YYYY"
    winning_numbers: List[int]
    number_range_min: int = 1
    number_range_max: int = 90

class DrawResponse(BaseModel):
    id: int
    lottery_name: str
    draw_date: str
    winning_numbers: List[int]
    number_range_min: int
    number_range_max: int

@router.post("/draws", response_model=dict)
async def create_draw(draw_data: DrawCreate, db: Session = Depends(get_db)):
    """Créer un nouveau tirage"""
    try:
        # Validation des numéros
        if len(draw_data.winning_numbers) < 5:
            raise HTTPException(status_code=400, detail="Au moins 5 numéros sont requis")
        
        # Vérifier que les numéros sont dans la plage
        for num in draw_data.winning_numbers:
            if num < draw_data.number_range_min or num > draw_data.number_range_max:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Le numéro {num} n'est pas dans la plage [{draw_data.number_range_min}-{draw_data.number_range_max}]"
                )
        
        # Convertir la date
        draw_date = datetime.strptime(draw_data.draw_date, "%d/%m/%Y")
        
        # Créer le tirage
        new_draw = Draw(
            lottery_name=draw_data.lottery_name,
            draw_date=draw_date,
            winning_numbers=draw_data.winning_numbers,
            number_range_min=draw_data.number_range_min,
            number_range_max=draw_data.number_range_max
        )
        
        db.add(new_draw)
        db.commit()
        db.refresh(new_draw)
        
        # Générer les combinaisons pour prévisualisation
        combinations = CombinationService.generate_combinations(draw_data.winning_numbers)
        classified = CombinationService.classify_combinations_by_universe(db, combinations)
        
        return {
            "message": "Tirage créé avec succès",
            "draw_id": new_draw.id,
            "total_combinations": len(combinations),
            "universes_preview": {k: len(v) for k, v in classified.items()}
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez DD/MM/YYYY")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/draws", response_model=List[dict])
async def get_draws(limit: int = 20, db: Session = Depends(get_db)):
    """Récupérer la liste des tirages"""
    draws = db.query(Draw).order_by(Draw.draw_date.desc()).limit(limit).all()
    
    return [
        {
            "id": draw.id,
            "lottery_name": draw.lottery_name,
            "draw_date": draw.draw_date.strftime("%d/%m/%Y"),
            "winning_numbers": draw.winning_numbers,
            "number_range": f"{draw.number_range_min}-{draw.number_range_max}"
        }
        for draw in draws
    ]

@router.get("/draws/{draw_id}")
async def get_draw(draw_id: int, db: Session = Depends(get_db)):
    """Récupérer un tirage spécifique"""
    draw = db.query(Draw).filter(Draw.id == draw_id).first()
    
    if not draw:
        raise HTTPException(status_code=404, detail="Tirage non trouvé")
    
    return {
        "id": draw.id,
        "lottery_name": draw.lottery_name,
        "draw_date": draw.draw_date.strftime("%d/%m/%Y"),
        "winning_numbers": draw.winning_numbers,
        "number_range_min": draw.number_range_min,
        "number_range_max": draw.number_range_max
    }

@router.delete("/draws/{draw_id}")
async def delete_draw(draw_id: int, db: Session = Depends(get_db)):
    """Supprimer un tirage"""
    draw = db.query(Draw).filter(Draw.id == draw_id).first()
    
    if not draw:
        raise HTTPException(status_code=404, detail="Tirage non trouvé")
    
    db.delete(draw)
    db.commit()
    
    return {"message": "Tirage supprimé avec succès"}

@router.get("/combinations/denomination/{denomination}")
async def get_combinations_by_denomination(
    denomination: str, 
    universe: str = None, 
    db: Session = Depends(get_db)
):
    """Récupérer toutes les combinaisons ayant une dénomination spécifique"""
    try:
        combinations = CombinationService.get_combinations_by_denomination(
            db, denomination, universe
        )
        
        if not combinations:
            raise HTTPException(
                status_code=404, 
                detail=f"Aucune combinaison trouvée pour la dénomination '{denomination}'"
            )
        
        # Organiser les données pour la réponse
        response = {
            "denomination": denomination,
            "universe": universe or "all",
            "total_occurrences": len(combinations),
            "details": combinations,
            "summary": {
                "universes": list(set(c["univers"] for c in combinations)),
                "formes": list(set(c["forme"] for c in combinations)),
                "chips": list(set(c["chip"] for c in combinations)),
                "engines": list(set(c["engine"] for c in combinations if c["engine"])),
                "beasties": list(set(c["beastie"] for c in combinations if c["beastie"])),
                "tomes": list(set(c["tome"] for c in combinations if c["tome"]))
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))