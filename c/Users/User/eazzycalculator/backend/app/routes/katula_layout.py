"""
Routes pour la disposition des tables Katula
"""
from fastapi import APIRouter, HTTPException
from app.services.katula_layout_service import KatulaLayoutService

router = APIRouter(prefix="/api/katula/layout", tags=["katula-layout"])
layout_service = KatulaLayoutService()

@router.get("/{universe}")
async def get_table_layout(universe: str):
    """Récupère la disposition de table pour un univers"""
    try:
        layout = layout_service.get_table_layout(universe)
        return layout_service.format_for_frontend(layout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{universe}/chip/{chip_id}")
async def get_chip_details(universe: str, chip_id: str):
    """Récupère les détails d'un chip spécifique"""
    try:
        details = layout_service.get_chip_details(universe, chip_id)
        if not details:
            raise HTTPException(status_code=404, detail="Chip non trouvé")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/neighbors/{chip_number}")
async def get_chip_neighbors(chip_number: int):
    """Récupère les voisins d'un chip"""
    from app.services.katula_table_service import KatulaTableService
    return KatulaTableService.get_chip_neighbors(chip_number)

@router.get("/optimal/{universe}")
async def get_optimal_positions(universe: str):
    """Récupère les positions optimales"""
    from app.services.katula_table_service import KatulaTableService
    return KatulaTableService.find_optimal_positions(universe)

@router.get("/distances")
async def get_distance_matrix():
    """Récupère la matrice des distances"""
    from app.services.katula_table_service import KatulaTableService
    return KatulaTableService.calculate_distance_matrix()