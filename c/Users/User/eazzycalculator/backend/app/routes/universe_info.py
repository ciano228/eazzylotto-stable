from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db

router = APIRouter()

@router.get("/katula/universe-info/{universe}")
async def get_universe_info(universe: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Récupère les informations de base d'un univers, notamment ses formes disponibles
    """
    try:
        # Récupérer les formes distinctes pour cet univers
        query = """
            SELECT DISTINCT forme
            FROM combinations 
            WHERE univers = :universe
            ORDER BY forme
        """
        result = db.execute(text(query), {"universe": universe})
        formes = [row[0] for row in result]
        
        # Compter le nombre de chips distincts
        count_query = """
            SELECT COUNT(DISTINCT chip)
            FROM combinations 
            WHERE univers = :universe
        """
        result = db.execute(text(count_query), {"universe": universe})
        total_chips = result.scalar() or 0
        
        return {
            "universe": universe,
            "formes": formes,
            "total_chips": total_chips,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des informations de l'univers {universe}: {str(e)}"
        )
