"""
Routes API pour le Journal Statistique
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database.connection import get_db
from app.services.journal_service import JournalService


router = APIRouter(tags=["journal"])


class DrawInput(BaseModel):
    numbers: List[int]
    universe: str = None


@router.post("/generate")
def generate_journal(draw: DrawInput, db: Session = Depends(get_db)):
    """Génère le journal statistique pour un tirage"""
    
    if len(draw.numbers) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 numéros requis")
    
    journal = JournalService.generate_full_journal(db, draw.numbers)
    
    return {
        "success": True,
        "data": journal
    }


@router.post("/validate-universe")
def validate_universe(draw: DrawInput, db: Session = Depends(get_db)):
    """Valide que toutes les combinaisons appartiennent à l'univers spécifié"""
    
    if not draw.universe:
        raise HTTPException(status_code=400, detail="Univers requis pour la validation")
    
    if len(draw.numbers) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 numéros requis")
    
    validation = JournalService.validate_draw_universe(db, draw.numbers, draw.universe)
    
    return {
        "success": True,
        "data": validation
    }


@router.get("/combination/{num1}/{num2}")
def get_combination_entry(num1: int, num2: int, db: Session = Depends(get_db)):
    """Récupère l'entrée de journal pour une combinaison spécifique"""
    
    entry = JournalService.generate_journal_entry(db, num1, num2)
    
    if "error" in entry:
        raise HTTPException(status_code=404, detail=entry["error"])
    
    return {
        "success": True,
        "data": entry
    }


@router.get("/mappings")
def get_mappings():
    """Récupère les mappings parite et unidos"""
    # Fallback mappings par défaut (ceux qui fonctionnaient dans integrated_server.py)
    parite_map = {
        "1": 'Pair-Pair', 
        "2": 'Pair-Impair', 
        "3": 'Impair-Pair', 
        "4": 'Impair-Impair'
    }
    unidos_map = {
        "1": 'U1-Bas-Bas', 
        "2": 'U2-Bas-Haut', 
        "3": 'U3-Haut-Bas', 
        "4": 'U4-Haut-Haut'
    }
    
    return {
        "success": True, 
        "parite": parite_map, 
        "unidos": unidos_map
    }
