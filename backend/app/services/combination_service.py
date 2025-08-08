from itertools import combinations
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.combination import Combination
from app.models.parite import Parite
from app.models.unidos import Unidos

class CombinationService:
    
    @staticmethod
    def generate_combinations(numbers: List[int]) -> List[tuple]:
        """Génère toutes les combinaisons de 2 numéros possibles"""
        return list(combinations(numbers, 2))
    
    @staticmethod
    def get_combination_info(db: Session, num1: int, num2: int) -> Dict[str, Any]:
        """Récupère les informations d'une combinaison depuis la DB avec jointures"""
        # S'assurer que num1 <= num2 pour la recherche
        if num1 > num2:
            num1, num2 = num2, num1
            
        # Import du modèle Chip
        from app.models.chip import Chip
        
        # Requête avec jointures pour récupérer les noms de parité, unidos et chip
        result = db.query(
            Combination,
            Parite.parite.label('parite_name'),
            Unidos.unidos.label('unidos_name'),
            Chip.chip_name.label('chip_name')
        ).outerjoin(
            Parite, Combination.parite_id == Parite.parite_id
        ).outerjoin(
            Unidos, Combination.unidos_id == Unidos.unidos_id
        ).outerjoin(
            Chip, Combination.chip_id == Chip.chip_id
        ).filter(
            Combination.num1 == num1,
            Combination.num2 == num2
        ).first()
        
        if result:
            combination, parite_name, unidos_name, chip_name = result
            
            # Debug logs
            print(f"DEBUG - Combination {num1}-{num2}:")
            print(f"  parite_id: {combination.parite_id}, parite_name: {parite_name}")
            print(f"  unidos_id: {combination.unidos_id}, unidos_name: {unidos_name}")
            print(f"  chip_id: {combination.chip_id}, chip_name: {chip_name}")
            
            return {
                "combination": f"{num1}-{num2}",
                "univers": combination.univers,
                "forme": combination.forme,
                "engine": combination.engine,
                "beastie": combination.beastie,
                "tome": combination.tome,
                "denomination": combination.denomination,
                "alpha_ranking": combination.alpha_ranking,
                "granque": combination.granque_name,
                "petique": combination.petique,
                "ligne": combination.ligne,
                "colonne": combination.colonne,
                "parite": parite_name or f"PARITE-{combination.parite_id}",
                "unidos": unidos_name or f"UNIDOS-{combination.unidos_id}",
                "chip": chip_name or f"CHIP-{combination.chip_id}",
                "combination_id": combination.combination_id
            }
        return None
    
    @staticmethod
    def classify_combinations_by_universe(db: Session, combinations: List[tuple]) -> Dict[str, List[Dict]]:
        """Classe les combinaisons par univers"""
        universes = {
            "mundo": [],
            "fruity": [],
            "trigga": [],
            "roaster": [],
            "sunshine": []
        }
        
        for combo in combinations:
            num1, num2 = combo
            combo_info = CombinationService.get_combination_info(db, num1, num2)
            
            if combo_info and combo_info["univers"] in universes:
                universes[combo_info["univers"]].append(combo_info)
        
        return universes
    
    @staticmethod
    def get_combinations_by_denomination(db: Session, denomination: str, universe: str = None) -> List[Dict[str, Any]]:
        """Récupère toutes les combinaisons ayant une dénomination spécifique - GÈRE LES DÉNOMINATIONS MULTIPLES"""
        
        # Si la dénomination contient "/", traiter chaque partie séparément
        if "/" in denomination:
            all_combinations = []
            denominations = [d.strip() for d in denomination.split("/")]
            
            for single_denomination in denominations:
                # Requête pour chaque dénomination individuelle
                query = db.query(Combination).filter(
                    Combination.denomination == single_denomination
                )
                
                if universe:
                    query = query.filter(Combination.univers == universe)
                
                results = query.all()
                
                for combination in results:
                    all_combinations.append({
                        "combination_id": combination.combination_id,
                        "num1": combination.num1,
                        "num2": combination.num2,
                        "combination": f"{combination.num1}-{combination.num2}",
                        "alpha_ranking": combination.alpha_ranking,
                        "univers": combination.univers,
                        "forme": combination.forme,
                        "denomination": combination.denomination,  # Dénomination individuelle
                        "original_search": denomination,  # Recherche originale avec "/"
                        "chip": combination.chip,
                        "engine": combination.engine,
                        "beastie": combination.beastie,
                        "tome": combination.tome
                    })
            
            # Trier par dénomination puis par alpha_ranking
            all_combinations.sort(key=lambda x: (x["denomination"], x["alpha_ranking"]))
            return all_combinations
        
        else:
            # Traitement normal pour une seule dénomination
            query = db.query(Combination).filter(
                Combination.denomination == denomination
            )
            
            if universe:
                query = query.filter(Combination.univers == universe)
            
            query = query.order_by(
                Combination.univers,
                Combination.forme,
                Combination.alpha_ranking,
                Combination.num1,
                Combination.num2
            )
            
            results = query.all()
            
            combinations = []
            for combination in results:
                combinations.append({
                    "combination_id": combination.combination_id,
                    "num1": combination.num1,
                    "num2": combination.num2,
                    "combination": f"{combination.num1}-{combination.num2}",
                    "alpha_ranking": combination.alpha_ranking,
                    "univers": combination.univers,
                    "forme": combination.forme,
                    "denomination": combination.denomination,
                    "chip": combination.chip,
                    "engine": combination.engine,
                    "beastie": combination.beastie,
                    "tome": combination.tome
                })
            
            return combinations