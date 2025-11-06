"""
Routes pour la Table de Katula Complète
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from ..services.katula_complete_service import KatulaCompleteService
from ..database.connection import get_db

router = APIRouter(prefix="/api/katula/complete", tags=["Katula Complete"])

@router.get("/table/{universe}")
async def get_complete_katula_table(universe: str):
    """Retourne la table Katula complète avec tous les éléments"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400, 
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        table = KatulaCompleteService.create_complete_katula_table(universe)
        
        return {
            "status": "success",
            "universe": universe,
            "table": table,
            "features": {
                "matrix_8x6": True,
                "granque_support": True,
                "tome_support": True,
                "petique_support": True,
                "quadrant_support": True,
                "side_panel": True,
                "filters": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/side-panel/{universe}")
async def get_side_panel_data(universe: str):
    """Retourne les données pour le side-panel de filtres"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        side_panel_data = KatulaCompleteService.get_side_panel_data(universe)
        
        return {
            "status": "success",
            "universe": universe,
            "side_panel": side_panel_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter/{universe}")
async def apply_filters(
    universe: str,
    filters: Dict[str, Any]
):
    """Applique les filtres à la table Katula"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        # Créer la table complète
        table = KatulaCompleteService.create_complete_katula_table(universe)
        
        # Appliquer les filtres
        filtered_result = KatulaCompleteService.apply_filters(table, filters)
        
        return {
            "status": "success",
            "universe": universe,
            "filtered_result": filtered_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chip/{universe}/{chip_number}")
async def get_chip_details(universe: str, chip_number: int):
    """Retourne les détails complets d'un chip"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        if chip_number < 1 or chip_number > 48:
            raise HTTPException(
                status_code=400,
                detail="Le numéro de chip doit être entre 1 et 48"
            )
        
        table = KatulaCompleteService.create_complete_katula_table(universe)
        chip_id = f"chip{chip_number}"
        
        if chip_id not in table["chip_positions"]:
            raise HTTPException(
                status_code=404,
                detail=f"Chip {chip_number} non trouvé"
            )
        
        chip_data = table["chip_positions"][chip_id]
        
        return {
            "status": "success",
            "universe": universe,
            "chip_number": chip_number,
            "chip_data": chip_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quadrants/{universe}")
async def get_quadrants_info(universe: str):
    """Retourne les informations sur les quadrants"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        table = KatulaCompleteService.create_complete_katula_table(universe)
        
        # Organiser par quadrants
        quadrants = {}
        for chip_id, chip_data in table["chip_positions"].items():
            quadrant = chip_data["quadrant"]
            petique = chip_data["petique"]
            
            if quadrant not in quadrants:
                quadrants[quadrant] = {
                    "chips": [],
                    "petiques": {},
                    "total_chips": 0
                }
            
            quadrants[quadrant]["chips"].append(chip_data)
            quadrants[quadrant]["total_chips"] += 1
            
            if petique not in quadrants[quadrant]["petiques"]:
                quadrants[quadrant]["petiques"][petique] = 0
            quadrants[quadrant]["petiques"][petique] += 1
        
        return {
            "status": "success",
            "universe": universe,
            "quadrants": quadrants,
            "summary": {
                "total_quadrants": len(quadrants),
                "chips_per_quadrant": {q: data["total_chips"] for q, data in quadrants.items()}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/granques/{universe}")
async def get_granques_info(universe: str):
    """Retourne les informations sur les granques"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        table = KatulaCompleteService.create_complete_katula_table(universe)
        
        # Organiser par granques
        granques = {}
        for chip_id, chip_data in table["chip_positions"].items():
            granque_base = chip_data["granque_name"].split('-')[0]
            
            if granque_base not in granques:
                granques[granque_base] = {
                    "chips": [],
                    "tomes": {},
                    "total_chips": 0
                }
            
            granques[granque_base]["chips"].append(chip_data)
            granques[granque_base]["total_chips"] += 1
            
            tome = chip_data["tome"]
            if tome not in granques[granque_base]["tomes"]:
                granques[granque_base]["tomes"][tome] = 0
            granques[granque_base]["tomes"][tome] += 1
        
        return {
            "status": "success",
            "universe": universe,
            "granques": granques,
            "summary": {
                "total_granques": len(granques),
                "chips_per_granque": {g: data["total_chips"] for g, data in granques.items()}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tomes/{universe}")
async def get_tomes_info(universe: str):
    """Retourne les informations sur les tomes"""
    try:
        if universe not in KatulaCompleteService.UNIVERSES:
            raise HTTPException(
                status_code=400,
                detail=f"Univers invalide. Univers disponibles: {KatulaCompleteService.UNIVERSES}"
            )
        
        table = KatulaCompleteService.create_complete_katula_table(universe)
        
        # Organiser par tomes
        tomes = {}
        for chip_id, chip_data in table["chip_positions"].items():
            tome = chip_data["tome"]
            
            if tome not in tomes:
                tomes[tome] = {
                    "chips": [],
                    "granques": {},
                    "petiques": {},
                    "total_chips": 0
                }
            
            tomes[tome]["chips"].append(chip_data)
            tomes[tome]["total_chips"] += 1
            
            # Compter granques
            granque_base = chip_data["granque_name"].split('-')[0]
            if granque_base not in tomes[tome]["granques"]:
                tomes[tome]["granques"][granque_base] = 0
            tomes[tome]["granques"][granque_base] += 1
            
            # Compter petiques
            petique = chip_data["petique"]
            if petique not in tomes[tome]["petiques"]:
                tomes[tome]["petiques"][petique] = 0
            tomes[tome]["petiques"][petique] += 1
        
        return {
            "status": "success",
            "universe": universe,
            "tomes": tomes,
            "summary": {
                "total_tomes": len(tomes),
                "chips_per_tome": {t: data["total_chips"] for t, data in tomes.items()}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))