"""
Routes API pour le Journal Statistique V2
Utilise PostgreSQL directement
"""

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from app.services.journal_service_v2 import JournalServiceV2


router = APIRouter(prefix="/api/journal", tags=["journal"])


class DrawInput(BaseModel):
    numbers: List[int]
    universe: str = None


@router.post("/generate")
def generate_journal(draw: DrawInput):
    """Génère le journal statistique pour un tirage"""
    
    if len(draw.numbers) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 numéros requis")
    
    journal = JournalServiceV2.generate_full_journal(draw.numbers)
    
    return {
        "success": True,
        "data": journal
    }


@router.post("/validate-universe")
def validate_universe(draw: DrawInput):
    """Valide que toutes les combinaisons appartiennent à l'univers spécifié"""
    
    if not draw.universe:
        raise HTTPException(status_code=400, detail="Univers requis pour la validation")
    
    if len(draw.numbers) < 2:
        raise HTTPException(status_code=400, detail="Au moins 2 numéros requis")
    
    validation = JournalServiceV2.validate_draw_universe(draw.numbers, draw.universe)
    
    return {
        "success": True,
        "data": validation
    }


@router.get("/combination/{num1}/{num2}")
def get_combination_entry(num1: int, num2: int):
    """Récupère l'entrée de journal pour une combinaison spécifique"""
    
    entry = JournalServiceV2.generate_journal_entry(num1, num2)
    
    if "error" in entry:
        raise HTTPException(status_code=404, detail=entry["error"])
    
    return {
        "success": True,
        "data": entry
    }
