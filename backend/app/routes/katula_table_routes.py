"""
Routes pour la Table de Katula Intégrée
API endpoints pour la matrice géométrique 8x6 avec données PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database_postgresql import get_db
from app.services.katula_table_integrated_service import KatulaTableIntegratedService

router = APIRouter(prefix="/api/katula-table", tags=["katula-table"])

@router.get("/health")
async def health_check():
    """Vérification de santé du service table Katula"""
    return {
        "status": "healthy",
        "service": "katula-table-integrated",
        "version": "1.0.0"
    }

@router.get("/{universe}")
async def get_katula_table(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère la table de Katula complète pour un univers
    Matrice 8x6 avec données PostgreSQL réelles
    """
    try:
        table = KatulaTableIntegratedService.get_complete_katula_table(db, universe)
        
        if "error" in table:
            raise HTTPException(status_code=500, detail=table["error"])
        
        return {
            "success": True,
            "universe": universe,
            "table": table
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la table: {str(e)}")

@router.get("/{universe}/chip/{chip_number}")
async def get_chip_details(
    universe: str,
    chip_number: int,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'un chip spécifique avec ses tiroirs et dénominations
    """
    try:
        chip_data = KatulaTableIntegratedService.get_chip_data(db, universe, chip_number)
        
        if "error" in chip_data:
            raise HTTPException(status_code=404, detail=chip_data["error"])
        
        return {
            "success": True,
            "chip_data": chip_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du chip: {str(e)}")

@router.get("/{universe}/analysis")
async def analyze_table_patterns(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Analyse les patterns et statistiques de la table de Katula
    """
    try:
        analysis = KatulaTableIntegratedService.analyze_table_patterns(db, universe)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@router.get("/{universe}/matrix")
async def get_matrix_structure(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère uniquement la structure matricielle 8x6 sans les données détaillées
    """
    try:
        table = KatulaTableIntegratedService.get_complete_katula_table(db, universe)
        
        if "error" in table:
            raise HTTPException(status_code=500, detail=table["error"])
        
        # Simplifier pour ne retourner que la structure
        matrix_structure = []
        for row in table["matrix"]:
            matrix_row = []
            for cell in row:
                matrix_row.append({
                    "chip_number": cell["chip_number"],
                    "position": cell["position"],
                    "row": cell["row"],
                    "column": cell["column"],
                    "has_data": len(cell.get("drawers", {})) > 0,
                    "drawer_count": sum(len(drawer) for drawer in cell.get("drawers", {}).values())
                })
            matrix_structure.append(matrix_row)
        
        return {
            "success": True,
            "universe": universe,
            "dimensions": table["dimensions"],
            "matrix": matrix_structure,
            "drawer_order": table["drawer_order"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la matrice: {str(e)}")

@router.get("/{universe}/zones")
async def get_zone_summary(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère un résumé par zones géométriques
    """
    try:
        analysis = KatulaTableIntegratedService.analyze_table_patterns(db, universe)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return {
            "success": True,
            "universe": universe,
            "zones": analysis["zone_analysis"],
            "quadrants": analysis["quadrant_analysis"],
            "drawers": analysis["drawer_analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des zones: {str(e)}")

@router.get("/utils/neighbors/{chip_number}")
async def get_chip_neighbors(chip_number: int):
    """
    Récupère les chips voisins d'un chip donné (utilitaire géométrique)
    """
    if chip_number < 1 or chip_number > 48:
        raise HTTPException(status_code=400, detail="Numéro de chip invalide (1-48)")
    
    row = ((chip_number - 1) // 6) + 1
    col = ((chip_number - 1) % 6) + 1
    
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 1 <= nr <= 8 and 1 <= nc <= 6:
                neighbor_chip = (nr - 1) * 6 + nc
                neighbors.append({
                    "chip_number": neighbor_chip,
                    "position": f"R{nr}C{nc}",
                    "direction": f"{'N' if dr < 0 else 'S' if dr > 0 else ''}{'W' if dc < 0 else 'E' if dc > 0 else ''}"
                })
    
    return {
        "success": True,
        "chip_number": chip_number,
        "position": f"R{row}C{col}",
        "neighbors": neighbors
    }

@router.get("/utils/distance/{chip1}/{chip2}")
async def calculate_chip_distance(chip1: int, chip2: int):
    """
    Calcule la distance entre deux chips
    """
    if chip1 < 1 or chip1 > 48 or chip2 < 1 or chip2 > 48:
        raise HTTPException(status_code=400, detail="Numéros de chips invalides (1-48)")
    
    # Positions des chips
    row1 = ((chip1 - 1) // 6) + 1
    col1 = ((chip1 - 1) % 6) + 1
    row2 = ((chip2 - 1) // 6) + 1
    col2 = ((chip2 - 1) % 6) + 1
    
    # Distance euclidienne
    distance = ((row2 - row1) ** 2 + (col2 - col1) ** 2) ** 0.5
    
    # Distance Manhattan
    manhattan_distance = abs(row2 - row1) + abs(col2 - col1)
    
    return {
        "success": True,
        "chip1": {"number": chip1, "position": f"R{row1}C{col1}"},
        "chip2": {"number": chip2, "position": f"R{row2}C{col2}"},
        "euclidean_distance": round(distance, 2),
        "manhattan_distance": manhattan_distance
    }