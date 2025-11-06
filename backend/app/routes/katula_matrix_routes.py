"""
Routes pour le service de matrice Katula
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..database.connection import get_db
from ..services.katula_matrix_service import KatulaMatrixService

router = APIRouter(prefix="/api/katula-matrix", tags=["Katula Matrix"])

@router.get("/extract")
async def extract_combinations_matrix(
    universe: str = Query("mundo", description="Univers (mundo/fruity)"),
    limit: int = Query(100, description="Nombre de combinaisons à extraire"),
    db: Session = Depends(get_db)
):
    """
    Extrait les données de la table combinations sous forme de matrice
    """
    try:
        result = KatulaMatrixService.extract_combinations_matrix(db, universe, limit)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/table-data")
async def get_katula_table_data(
    universe: str = Query("mundo", description="Univers (mundo/fruity)"),
    db: Session = Depends(get_db)
):
    """
    Récupère les données de la table_de_katula ou combinations
    """
    try:
        result = KatulaMatrixService.get_katula_table_data(db, universe)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/formatted")
async def get_formatted_data(
    universe: str = Query("mundo", description="Univers (mundo/fruity)"),
    format_type: str = Query("matrix", description="Type de format (matrix/list)"),
    db: Session = Depends(get_db)
):
    """
    Retourne les données formatées pour le service katula-table
    """
    try:
        result = KatulaMatrixService.format_for_katula_service(db, universe, format_type)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.get("/matrix-8x6")
async def get_matrix_8x6(
    universe: str = Query("mundo", description="Univers (mundo/fruity)"),
    db: Session = Depends(get_db)
):
    """
    Retourne une matrice 8x6 formatée pour katula-table
    """
    try:
        result = KatulaMatrixService.format_for_katula_service(db, universe, "matrix")
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "universe": result["universe"],
            "matrix": result["matrix"],
            "dimensions": result["dimensions"],
            "timestamp": result["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")