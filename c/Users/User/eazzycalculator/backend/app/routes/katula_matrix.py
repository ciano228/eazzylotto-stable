from typing import Dict
from sqlalchemy.orm import Session
from app.database.connection import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.models.combinations import Combination

router = APIRouter()

@router.get("/katula/matrix/{universe}")
async def get_katula_matrix(universe: str, db: Session = Depends(get_db)) -> Dict:
    """Retourne la structure matricielle complète des chips pour un univers donné"""
    chips_matrix = {}
    try:
        # Extraire dynamiquement les formes disponibles pour l'univers
        formes_query = db.query(Combination.forme).filter(
            Combination.univers == universe.lower()
        ).distinct()
        formes_list = [f[0] for f in formes_query if f[0]]
        
        # Extraire toutes les données des chips pour cet univers
        rows = db.query(Combination).filter(
            Combination.univers == universe.lower()
        ).order_by(Combination.chip).all()
        
        # Organiser les données par chip
        for row in rows:
            chip_num = row.chip
            if chip_num not in chips_matrix:
                chips_matrix[chip_num] = {
                    "chip": chip_num,
                    "colonne": row.colonne,
                    "ligne": row.ligne,
                    "petique": row.petique,
                    "granque": row.granque_name,
                    "tome": row.tome,
                    "univers": row.univers,
                    "formes": {},
                    "denominations": set(),
                }
            
            # Ajouter la forme et la dénomination
            if row.forme and row.denomination:
                if row.forme not in chips_matrix[chip_num]["formes"]:
                    chips_matrix[chip_num]["formes"][row.forme] = set()
                chips_matrix[chip_num]["formes"][row.forme].add(row.denomination)
                chips_matrix[chip_num]["denominations"].add(row.denomination)
        
        # Convertir les sets en listes pour la sérialisation JSON
        for chip in chips_matrix.values():
            chip["denominations"] = sorted(list(chip["denominations"]))
            for forme in chip["formes"]:
                chip["formes"][forme] = sorted(list(chip["formes"][forme]))
        
        return {
            "chips": chips_matrix,
            "universe": universe,
            "total_chips": len(chips_matrix),
            "formes": sorted(formes_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du chargement de la matrice Katula pour l'univers {universe}: {str(e)}"
        )
