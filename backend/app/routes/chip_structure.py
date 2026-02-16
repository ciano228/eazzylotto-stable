"""
Endpoint pour récupérer la structure réelle des drawers par chip
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from collections import defaultdict

router = APIRouter()

@router.get("/chip-drawers-structure-fixed")
async def get_chip_drawers_structure(
    universe: str = Query("mundo", description="Univers (fruity, mundo, etc.)")
):
    """
    Récupère la structure réelle des drawers pour chaque chip d'un univers
    
    Retourne:
    {
      "chip1": [
        {"drawer_name": "drawer1", "forme": "carre", "denomination": "..."},
        {"drawer_name": "drawer2", "forme": "triangle", "denomination": "..."},
        ...
      ],
      "chip2": [...],
      ...
    }
    """
    try:
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            from sqlalchemy import text
            
            # Query pour récupérer les DRAWERS UNIQUES de cet univers
            # GROUP BY pour dédupliquer les entrées multiples par alpha_ranking
            query = text("""
                SELECT 
                    chip,
                    drawer_name,
                    drawer,
                    forme,
                    MIN(denomination) as denomination
                FROM combinations
                WHERE univers = :universe
                AND drawer_name IS NOT NULL
                GROUP BY chip, drawer_name, drawer, forme
                ORDER BY chip, drawer_name
            """)
            
            result = db.execute(query, {"universe": universe})
            rows = result.fetchall()
            
            # Organiser par chip
            chip_structure = defaultdict(list)
            
            for row in rows:
                chip, drawer_name, drawer, forme, denomination = row
                
                # Assurer que chip est une string
                chip_key = str(chip)
                
                chip_structure[chip_key].append({
                    "drawer_name": drawer_name,
                    "drawer": drawer,
                    "forme": forme,
                    "denomination": denomination
                })
            
            # Convertir en dict normal
            chip_structure_dict = dict(chip_structure)
            
            # Compter les stats
            total_chips = len(chip_structure_dict)
            total_drawers = sum(len(drawers) for drawers in chip_structure_dict.values())
            
            return {
                "status": "success",
                "universe": universe,
                "chip_structure": chip_structure_dict,
                "statistics": {
                    "total_chips": total_chips,
                    "total_drawers": total_drawers,
                    "avg_drawers_per_chip": round(total_drawers / total_chips, 2) if total_chips > 0 else 0
                }
            }
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR:chip_structure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération structure: {str(e)}")
