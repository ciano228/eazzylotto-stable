"""
Routes API pour les Poids Structurels Katula
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.services.structural_weight_service import StructuralWeightService

router = APIRouter()


@router.get("/structural-weights/{universe}/{attribute_type}/{attribute_value}")
async def get_structural_weight(
    universe: str,
    attribute_type: str,
    attribute_value: str,
    db: Session = Depends(get_db)
):
    """
    Récupère le poids structurel pour un élément spécifique
    
    Args:
        universe: Univers (mundo, fruity, trigga, roaster, sunshine)
        attribute_type: Type d'attribut (chip, ligne, colonne, forme, etc.)
        attribute_value: Valeur de l'attribut (chip_5, ligne1, carre, etc.)
    
    Returns:
        {
            "universe": "mundo",
            "attribute_type": "chip",
            "attribute_value": "chip_5",
            "cardinality": 15,
            "total_universe": 544,
            "probability": 0.027574,
            "expected_gap": 36.27,
            "weight": 0.027574
        }
    """
    try:
        weight = StructuralWeightService.get_structural_weight(
            db, universe, attribute_type, attribute_value
        )
        return weight
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural-weights/{universe}/{attribute_type}")
async def get_all_weights_for_attribute(
    universe: str,
    attribute_type: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les poids structurels pour toutes les valeurs d'un attribut
    
    Args:
        universe: Univers
        attribute_type: Type d'attribut
    
    Returns:
        {
            "chip_5": {...},
            "chip_10": {...},
            ...
        }
    """
    try:
        weights = StructuralWeightService.get_all_weights_for_attribute(
            db, universe, attribute_type
        )
        return weights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural-weights/{universe}/statistics")
async def get_universe_statistics(
    universe: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques globales d'un univers
    
    Returns:
        {
            "universe": "mundo",
            "total_combinations": 544,
            "attributes": {
                "chip": {
                    "count": 48,
                    "values": {...}
                },
                ...
            }
        }
    """
    try:
        stats = StructuralWeightService.get_universe_statistics(db, universe)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural-weights/gap-score")
async def calculate_gap_score(
    current_gap: int = Query(..., description="Gap actuel observé"),
    universe: str = Query(..., description="Univers"),
    attribute_type: str = Query(..., description="Type d'attribut"),
    attribute_value: str = Query(..., description="Valeur de l'attribut"),
    db: Session = Depends(get_db)
):
    """
    Calcule le score de gap normalisé
    
    Returns:
        {
            "current_gap": 40,
            "expected_gap": 36.27,
            "gap_score": 1.10,
            "interpretation": "froid",
            "details": {...}
        }
    """
    try:
        score = StructuralWeightService.calculate_gap_score(
            current_gap, universe, attribute_type, attribute_value, db
        )
        
        weight = StructuralWeightService.get_structural_weight(
            db, universe, attribute_type, attribute_value
        )
        
        # Interprétation
        if score < 0.8:
            interpretation = "très chaud"
        elif score < 1.0:
            interpretation = "chaud"
        elif score < 1.2:
            interpretation = "normal"
        elif score < 1.5:
            interpretation = "froid"
        else:
            interpretation = "très froid"
        
        return {
            "current_gap": current_gap,
            "expected_gap": weight['expected_gap'],
            "gap_score": round(score, 2),
            "interpretation": interpretation,
            "details": weight
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural-weights/predict-appearance")
async def predict_appearance(
    current_gap: int = Query(..., description="Gap actuel"),
    n_draws: int = Query(..., description="Nombre de tirages futurs"),
    universe: str = Query(..., description="Univers"),
    attribute_type: str = Query(..., description="Type d'attribut"),
    attribute_value: str = Query(..., description="Valeur de l'attribut"),
    db: Session = Depends(get_db)
):
    """
    Prédit la probabilité d'apparition dans les N prochains tirages
    
    Returns:
        {
            "current_gap": 40,
            "n_draws": 10,
            "probability": 0.243,
            "percentage": "24.3%",
            "details": {...}
        }
    """
    try:
        probability = StructuralWeightService.predict_appearance_probability(
            current_gap, n_draws, universe, attribute_type, attribute_value, db
        )
        
        weight = StructuralWeightService.get_structural_weight(
            db, universe, attribute_type, attribute_value
        )
        
        return {
            "current_gap": current_gap,
            "n_draws": n_draws,
            "probability": probability,
            "percentage": f"{probability * 100:.1f}%",
            "expected_gap": weight['expected_gap'],
            "details": weight
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/structural-weights/cardinality")
async def get_cardinality(
    universe: str = Query(..., description="Univers"),
    attribute_type: str = Query(..., description="Type d'attribut"),
    attribute_value: str = Query(..., description="Valeur de l'attribut"),
    db: Session = Depends(get_db)
):
    """
    Récupère la cardinalité (nombre de combinaisons) d'un élément
    
    Returns:
        {
            "universe": "mundo",
            "attribute_type": "chip",
            "attribute_value": "chip_5",
            "cardinality": 15,
            "total_universe": 544,
            "percentage": "2.76%"
        }
    """
    try:
        cardinality = StructuralWeightService.calculate_cardinality(
            db, universe, attribute_type, attribute_value
        )
        
        total = StructuralWeightService.get_total_combinations(universe)
        percentage = (cardinality / total * 100) if total > 0 else 0
        
        return {
            "universe": universe,
            "attribute_type": attribute_type,
            "attribute_value": attribute_value,
            "cardinality": cardinality,
            "total_universe": total,
            "percentage": f"{percentage:.2f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
