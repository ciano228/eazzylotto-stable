"""
Service de Journal Statistique avec validation BD
Utilise les vraies données de la base de données
"""

from typing import Dict, List, Any, Tuple
from itertools import combinations
from sqlalchemy.orm import Session
from app.services.combination_service import CombinationService


class JournalService:
    """Service pour générer des journaux statistiques basés sur les vraies données BD"""
    
    @staticmethod
    def generate_journal_entry(db: Session, num1: int, num2: int) -> Dict[str, Any]:
        """Génère une entrée de journal pour une combinaison en utilisant les vraies données BD"""
        
        # Sécurité: s'assurer que ce sont des entiers
        try:
            num1_int = int(num1)
            num2_int = int(num2)
        except (ValueError, TypeError):
            return {
                "error": f"Numéros invalides: {num1}, {num2}",
                "status": "no_hold"
            }
            
        # S'assurer que num1 < num2 pour la requête BD (les combinaisons sont stockées triées)
        n1, n2 = min(num1_int, num2_int), max(num1_int, num2_int)
        
        # Récupérer les vraies données depuis la BD
        combo_info = CombinationService.get_combination_info(db, n1, n2)
        
        if not combo_info:
            return {
                "error": f"Combinaison {num1}-{num2} non trouvée dans la base de données",
                "combination": [num1, num2],
                "num1": num1,
                "num2": num2,
                "status": "no_hold",
                "univers": "N/A",
                "denomination": "N/A"
            }
        
        # Construire l'entrée du journal avec la structure attendue par le frontend
        return {
            "combination": [num1, num2],
            "combination_str": f"{num1}-{num2}",
            "num1": num1,
            "num2": num2,
            "univers": combo_info.get("univers"),
            "denomination": combo_info.get("denomination"),
            "status": "normal",
            "parite_id": combo_info.get("parite_id"),
            "unidos_id": combo_info.get("unidos_id"),
            "region": combo_info.get("region"),
            "quartier": combo_info.get("quartier"),
            "gentile": combo_info.get("gentile") or combo_info.get("gentillee"), # Support both
            "num1_analysis": {
                "number": num1,
                "alpha_ranking": combo_info.get("alpha_ranking"),
                "granque_name": combo_info.get("granque"),
                "petique": combo_info.get("petique"),
                "chip": combo_info.get("chip"),
                "forme": combo_info.get("forme"),
                "engine": combo_info.get("engine"),
                "beastie": combo_info.get("beastie"),
                "tome": combo_info.get("tome"),
                "position": {
                    "ligne": combo_info.get("ligne"),
                    "colonne": combo_info.get("colonne")
                }
            },
            "num2_analysis": {
                "number": num2
            },
            "combination_id": combo_info.get("combination_id")
        }
    
    @staticmethod
    def generate_full_journal(db: Session, numbers: List[int]) -> Dict[str, Any]:
        """Génère le journal complet pour un tirage avec toutes les combinaisons"""
        
        # Générer toutes les combinaisons 2 à 2
        combos = list(combinations(numbers, 2))
        
        journal_entries = []
        errors = []
        
        for num1, num2 in combos:
            entry = JournalService.generate_journal_entry(db, num1, num2)
            
            # On inclut tout dans journal_entries pour que le frontend puisse afficher les NO-HOLD
            journal_entries.append(entry)
            
            if "error" in entry:
                errors.append(entry)
        
        # Analyser par univers
        by_universe = {}
        for entry in journal_entries:
            univers = entry.get("univers", "N/A")
            if univers not in by_universe:
                by_universe[univers] = []
            by_universe[univers].append(entry)
        
        # Analyser par caractère (seulement pour les entrées valides)
        valid_entries = [e for e in journal_entries if "error" not in e]
        character_analysis = JournalService._analyze_by_characters(valid_entries)
        
        return {
            "input_numbers": numbers,
            "total_combinations": len(combos),
            "valid_entries": len(valid_entries),
            "errors": len(errors),
            "journal_entries": journal_entries,
            "error_details": errors,
            "by_universe": by_universe,
            "character_analysis": character_analysis
        }
    
    @staticmethod
    def _analyze_by_characters(journal_entries: List[Dict]) -> Dict[str, Any]:
        """Analyse les entrées par caractère (tome, forme, granque, etc.)"""
        
        analysis = {
            "tome": {},
            "forme": {},
            "granque": {},
            "petique": {},
            "univers": {},
            "denomination": {}
        }
        
        for entry in journal_entries:
            # Tome
            tome = entry.get("tome")
            if tome:
                if tome not in analysis["tome"]:
                    analysis["tome"][tome] = {"count": 0, "combinations": []}
                analysis["tome"][tome]["count"] += 1
                analysis["tome"][tome]["combinations"].append(entry["combination"])
            
            # Forme
            forme = entry.get("forme")
            if forme:
                if forme not in analysis["forme"]:
                    analysis["forme"][forme] = {"count": 0, "combinations": []}
                analysis["forme"][forme]["count"] += 1
                analysis["forme"][forme]["combinations"].append(entry["combination"])
            
            # Granque
            granque = entry.get("granque")
            if granque:
                if granque not in analysis["granque"]:
                    analysis["granque"][granque] = {"count": 0, "combinations": []}
                analysis["granque"][granque]["count"] += 1
                analysis["granque"][granque]["combinations"].append(entry["combination"])
            
            # Petique
            petique = entry.get("petique")
            if petique:
                if petique not in analysis["petique"]:
                    analysis["petique"][petique] = {"count": 0, "combinations": []}
                analysis["petique"][petique]["count"] += 1
                analysis["petique"][petique]["combinations"].append(entry["combination"])
            
            # Univers
            univers = entry.get("univers")
            if univers:
                if univers not in analysis["univers"]:
                    analysis["univers"][univers] = {"count": 0, "combinations": []}
                analysis["univers"][univers]["count"] += 1
                analysis["univers"][univers]["combinations"].append(entry["combination"])
            
            # Denomination
            denomination = entry.get("denomination")
            if denomination:
                if denomination not in analysis["denomination"]:
                    analysis["denomination"][denomination] = {"count": 0, "combinations": []}
                analysis["denomination"][denomination]["count"] += 1
                analysis["denomination"][denomination]["combinations"].append(entry["combination"])
        
        return analysis
    
    @staticmethod
    def validate_draw_universe(db: Session, numbers: List[int], expected_universe: str) -> Dict[str, Any]:
        """Valide que toutes les combinaisons d'un tirage appartiennent à l'univers attendu"""
        
        journal = JournalService.generate_full_journal(db, numbers)
        
        # Vérifier les univers
        invalid_combinations = []
        for entry in journal["journal_entries"]:
            if entry["univers"] != expected_universe:
                invalid_combinations.append({
                    "combination": entry["combination"],
                    "expected_universe": expected_universe,
                    "actual_universe": entry["univers"]
                })
        
        is_valid = len(invalid_combinations) == 0
        
        return {
            "is_valid": is_valid,
            "expected_universe": expected_universe,
            "total_combinations": journal["total_combinations"],
            "valid_combinations": journal["valid_entries"] - len(invalid_combinations),
            "invalid_combinations": invalid_combinations,
            "universe_distribution": journal["character_analysis"]["univers"]
        }
