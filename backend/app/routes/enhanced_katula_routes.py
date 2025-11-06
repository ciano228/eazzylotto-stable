"""
Routes améliorées pour la vraie structure Katula avec formes et dénominations réelles
"""
from fastapi import APIRouter, HTTPException
from app.services.enhanced_real_katula_service import enhanced_real_katula_service

router = APIRouter()

@router.get("/katula/enhanced/{univers}")
async def get_enhanced_katula_data(univers: str):
    """Récupérer les données Katula enrichies avec la vraie structure"""
    try:
        result = enhanced_real_katula_service.get_enhanced_table_data(univers)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": f"Données enrichies pour l'univers {univers}",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/katula/comparison/{univers}")
async def compare_bd_vs_real(univers: str):
    """Comparer les données BD vs structure réelle"""
    try:
        result = enhanced_real_katula_service.compare_bd_vs_real_structure(univers)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": f"Comparaison BD vs structure réelle pour {univers}",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/katula/chip/{univers}/{chip}")
async def get_refined_chip(univers: str, chip: str):
    """Affichage raffiné d'un chip avec vraies formes et dénominations"""
    try:
        result = enhanced_real_katula_service.get_refined_chip_display(univers, chip)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "message": f"Affichage raffiné du {chip} dans l'univers {univers}",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/katula/real-structure/{univers}")
async def get_real_structure_info(univers: str):
    """Informations sur la structure réelle disponible"""
    try:
        if not enhanced_real_katula_service.real_structure:
            raise HTTPException(status_code=404, detail="Structure réelle non chargée")
        
        if univers not in enhanced_real_katula_service.real_structure:
            available_universes = list(enhanced_real_katula_service.real_structure.keys())
            raise HTTPException(
                status_code=404, 
                detail=f"Univers {univers} non trouvé. Disponibles: {available_universes}"
            )
        
        universe_data = enhanced_real_katula_service.real_structure[univers]
        
        # Statistiques de la structure réelle
        total_chips = len(universe_data["chips"])
        total_compartments = sum(chip["nb_compartiments"] for chip in universe_data["chips"].values())
        
        # Toutes les dénominations
        all_denominations = []
        for chip_data in universe_data["chips"].values():
            for comp in chip_data["compartiments_verticaux"]:
                if comp["denomination"] not in all_denominations:
                    all_denominations.append(comp["denomination"])
        
        return {
            "success": True,
            "message": f"Structure réelle pour l'univers {univers}",
            "data": {
                "univers": univers,
                "statistiques": {
                    "total_chips": total_chips,
                    "total_compartiments": total_compartments,
                    "total_formes": len(universe_data["formes_disponibles"]),
                    "total_petiques": len(universe_data["petiques_disponibles"]),
                    "total_denominations": len(all_denominations)
                },
                "formes_geometriques_reelles": universe_data["formes_disponibles"],
                "zones_petiques_reelles": universe_data["petiques_disponibles"],
                "denominations_reelles": all_denominations[:20],  # Première 20
                "exemple_chip": {
                    "chip_id": "chip1",
                    "structure": universe_data["chips"].get("chip1", {})
                }
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/katula/validate-mapping/{univers}")
async def validate_bd_mapping(univers: str):
    """Valider le mapping entre BD et structure réelle"""
    try:
        comparison = enhanced_real_katula_service.compare_bd_vs_real_structure(univers)
        
        if "error" in comparison:
            raise HTTPException(status_code=500, detail=comparison["error"])
        
        # Analyser la qualité du mapping
        bd_data = comparison["donnees_bd"]
        real_data = comparison.get("donnees_reelles", {})
        
        if "error" in real_data:
            mapping_quality = "Structure réelle non disponible"
            recommendations = ["Vérifier la disponibilité du fichier katula_structure_reelle.json"]
        else:
            # Calculer la qualité du mapping
            forme_match_rate = 0
            if bd_data["formes"] and real_data["formes"]:
                matching_formes = len(set(bd_data["formes"]) & set(real_data["formes"]))
                forme_match_rate = (matching_formes / len(real_data["formes"])) * 100
            
            if forme_match_rate >= 80:
                mapping_quality = "Excellent"
            elif forme_match_rate >= 60:
                mapping_quality = "Bon"
            elif forme_match_rate >= 40:
                mapping_quality = "Moyen"
            else:
                mapping_quality = "Faible"
            
            recommendations = []
            if forme_match_rate < 100:
                recommendations.append("Synchroniser les formes manquantes entre BD et structure réelle")
            if bd_data["total_chips"] != real_data["total_chips"]:
                recommendations.append("Vérifier la cohérence du nombre de chips")
            if not recommendations:
                recommendations.append("Mapping optimal - aucune action requise")
        
        return {
            "success": True,
            "message": f"Validation du mapping pour l'univers {univers}",
            "data": {
                "univers": univers,
                "qualite_mapping": mapping_quality,
                "taux_correspondance_formes": f"{forme_match_rate:.1f}%" if 'forme_match_rate' in locals() else "N/A",
                "recommandations": recommendations,
                "details_comparison": comparison
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")