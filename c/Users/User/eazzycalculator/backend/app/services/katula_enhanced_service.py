"""
Service de Table de Katula Amélioré
Récupère les vraies formes depuis la table combinations avec les relations réelles
"""
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.services.katula_table_service import KatulaTableService

class KatulaEnhancedService:
    """
    Service amélioré pour la Table de Katula avec vraies données
    """
    
    @staticmethod
    def get_universe_formes(db: Session, universe: str = "mundo") -> List[str]:
        """Récupère les vraies formes d'un univers depuis la table combinations"""
        
        try:
            query = """
                SELECT DISTINCT forme
                FROM combinations 
                WHERE univers = :universe 
                AND forme IS NOT NULL
                ORDER BY forme
            """
            
            result = db.execute(text(query), {"universe": universe})
            formes = [row.forme for row in result.fetchall()]
            
            print(f"🎨 Formes trouvées pour {universe}: {formes}")
            return formes
            
        except Exception as e:
            print(f"❌ Erreur récupération formes {universe}: {e}")
            # Fallback par défaut
            return ['carre', 'triangle', 'cercle', 'rectangle']
    
    @staticmethod
    def get_chip_forme_combinations(
        db: Session, 
        universe: str, 
        chip_number: int
    ) -> Dict[str, Any]:
        """Récupère toutes les combinaisons d'un chip avec leurs formes"""
        
        try:
            query = """
                SELECT 
                    combination_id,
                    num1, 
                    num2,
                    forme,
                    chip,
                    chip_id,
                    created_at
                FROM combinations 
                WHERE univers = :universe 
                AND chip_id = :chip_number
                ORDER BY combination_id DESC
                LIMIT 20
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "chip_number": chip_number
            })
            
            combinations = []
            formes_count = {}
            
            for row in result.fetchall():
                combo = {
                    "combination_id": row.combination_id,
                    "numbers": f"{row.num1}-{row.num2}",
                    "forme": row.forme,
                    "chip": row.chip,
                    "chip_id": row.chip_id,
                    "date": row.created_at.isoformat() if row.created_at else None
                }
                combinations.append(combo)
                
                # Compter les formes
                forme = row.forme or 'unknown'
                formes_count[forme] = formes_count.get(forme, 0) + 1
            
            return {
                "chip_number": chip_number,
                "universe": universe,
                "total_combinations": len(combinations),
                "combinations": combinations,
                "formes_frequency": formes_count,
                "most_frequent_forme": max(formes_count.items(), key=lambda x: x[1])[0] if formes_count else None
            }
            
        except Exception as e:
            print(f"❌ Erreur chip {chip_number} pour {universe}: {e}")
            return {
                "chip_number": chip_number,
                "universe": universe,
                "error": str(e),
                "combinations": []
            }
    
    @staticmethod
    def create_enhanced_katula_table(db: Session, universe: str = "mundo") -> Dict[str, Any]:
        """Crée une Table de Katula enrichie avec les vraies données"""
        
        try:
            # Créer la table de base
            base_table = KatulaTableService.create_katula_table(universe)
            
            # Récupérer les vraies formes
            real_formes = KatulaEnhancedService.get_universe_formes(db, universe)
            
            # Enrichir chaque chip avec ses données réelles
            enhanced_chips = {}
            
            for chip_id, chip_info in base_table["chip_positions"].items():
                chip_number = chip_info["chip_number"]
                
                # Récupérer les combinaisons réelles pour ce chip
                chip_data = KatulaEnhancedService.get_chip_forme_combinations(
                    db, universe, chip_number
                )
                
                # Enrichir les informations du chip
                enhanced_chip = {
                    **chip_info,
                    "real_combinations": chip_data["combinations"],
                    "formes_frequency": chip_data["formes_frequency"],
                    "most_frequent_forme": chip_data["most_frequent_forme"],
                    "total_appearances": chip_data["total_combinations"],
                    "activity_level": KatulaEnhancedService._calculate_activity_level(
                        chip_data["total_combinations"]
                    )
                }
                
                enhanced_chips[chip_id] = enhanced_chip
            
            # Créer la table enrichie
            enhanced_table = {
                **base_table,
                "real_formes": real_formes,
                "total_formes": len(real_formes),
                "enhanced_chips": enhanced_chips,
                "universe_stats": KatulaEnhancedService._calculate_universe_stats(
                    enhanced_chips, real_formes
                )
            }
            
            return enhanced_table
            
        except Exception as e:
            print(f"❌ Erreur création table enrichie {universe}: {e}")
            return KatulaTableService.create_katula_table(universe)
    
    @staticmethod
    def _calculate_activity_level(total_combinations: int) -> str:
        """Calcule le niveau d'activité d'un chip"""
        
        if total_combinations == 0:
            return "inactive"
        elif total_combinations <= 2:
            return "low"
        elif total_combinations <= 5:
            return "medium"
        elif total_combinations <= 10:
            return "high"
        else:
            return "very_high"
    
    @staticmethod
    def _calculate_universe_stats(enhanced_chips: Dict, real_formes: List[str]) -> Dict[str, Any]:
        """Calcule les statistiques globales de l'univers"""
        
        total_combinations = sum(
            chip.get("total_appearances", 0) 
            for chip in enhanced_chips.values()
        )
        
        active_chips = len([
            chip for chip in enhanced_chips.values() 
            if chip.get("total_appearances", 0) > 0
        ])
        
        # Statistiques par forme
        forme_stats = {}
        for forme in real_formes:
            forme_count = 0
            for chip in enhanced_chips.values():
                forme_freq = chip.get("formes_frequency", {})
                forme_count += forme_freq.get(forme, 0)
            forme_stats[forme] = forme_count
        
        return {
            "total_combinations": total_combinations,
            "active_chips": active_chips,
            "inactive_chips": 48 - active_chips,
            "formes_distribution": forme_stats,
            "most_popular_forme": max(forme_stats.items(), key=lambda x: x[1])[0] if forme_stats else None,
            "average_combinations_per_chip": total_combinations / 48 if total_combinations > 0 else 0
        }
    
    @staticmethod
    def get_forme_patterns(db: Session, universe: str, forme: str) -> Dict[str, Any]:
        """Analyse les patterns d'une forme spécifique"""
        
        try:
            query = """
                SELECT 
                    chip_id,
                    COUNT(*) as frequency,
                    MIN(combination_id) as first_appearance,
                    MAX(combination_id) as last_appearance,
                    AVG(CAST(combination_id AS FLOAT)) as avg_position
                FROM combinations 
                WHERE univers = :universe 
                AND forme = :forme
                GROUP BY chip_id
                ORDER BY frequency DESC
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "forme": forme
            })
            
            patterns = []
            for row in result.fetchall():
                patterns.append({
                    "chip_id": row.chip_id,
                    "frequency": row.frequency,
                    "first_appearance": row.first_appearance,
                    "last_appearance": row.last_appearance,
                    "avg_position": round(row.avg_position, 2),
                    "activity_span": row.last_appearance - row.first_appearance
                })
            
            return {
                "universe": universe,
                "forme": forme,
                "total_appearances": sum(p["frequency"] for p in patterns),
                "active_chips": len(patterns),
                "chip_patterns": patterns,
                "most_active_chip": patterns[0]["chip_id"] if patterns else None,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "universe": universe,
                "forme": forme,
                "error": str(e)
            }