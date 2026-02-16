"""
Service de Journal Statistique V2
Adapté pour PostgreSQL katooling_main_system
Utilise directement psycopg2 pour éviter les problèmes de modèles SQLAlchemy
"""

from typing import Dict, List, Any
from itertools import combinations
import psycopg2
from psycopg2.extras import RealDictCursor


class JournalServiceV2:
    """Service pour générer des journaux statistiques basés sur PostgreSQL"""
    
    # Configuration PostgreSQL
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    @staticmethod
    def _get_connection():
        """Crée une connexion à PostgreSQL"""
        return psycopg2.connect(**JournalServiceV2.DB_CONFIG)
    
    @staticmethod
    def generate_journal_entry(num1: int, num2: int, conn=None) -> Dict[str, Any]:
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
        
        # Utiliser la connexion fournie ou en créer une nouvelle
        internal_conn = False
        if conn is None:
            conn = JournalServiceV2._get_connection()
            internal_conn = True
            
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Requête pour récupérer la combinaison (incluant drawer_name si présent)
            cursor.execute("""
                SELECT 
                    combination_id, num1, num2, univers, forme, 
                    granque_name, petique, tome, denomination,
                    engine, beastie, chip, ligne, colonne,
                    alpha_ranking, parite_id, unidos_id, chip_id,
                    quartier, region, gentile, base_name,
                    cell_num1, cell_num2, position_num1, position_num2,
                    lot_num1, lot_num2, ash_num1, ash_num2,
                    room_num1, room_num2, col_num1, col_num2,
                    combination, row_number, denomination_id,
                    denomination_row_number, forme_id, univers_id, drawer, drawer_name
                FROM combinations 
                WHERE num1 = %s AND num2 = %s
            """, (n1, n2))
            
            row = cursor.fetchone()
            
            if not row:
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
                "univers": row.get("univers"),
                "denomination": row.get("denomination"),
                "status": "normal",
                "parite_id": row.get("parite_id"),
                "unidos_id": row.get("unidos_id"),
                "region": row.get("region"),
                "quartier": row.get("quartier"),
                "gentile": row.get("gentile"),
                "num1_analysis": {
                    "number": num1,
                    "alpha_ranking": row.get("alpha_ranking"),
                    "granque_name": row.get("granque_name"),
                    "petique": row.get("petique"),
                    "chip": row.get("chip"),
                    "forme": row.get("forme"),
                    "engine": row.get("engine"),
                    "beastie": row.get("beastie"),
                    "tome": row.get("tome"),
                    "position": {
                        "ligne": row.get("ligne"),
                        "colonne": row.get("colonne")
                    }
                },
                "num2_analysis": {
                    "number": num2
                },
                "combination_id": row.get("combination_id")
            }
            
        finally:
            if internal_conn:
                conn.close()
    
    @staticmethod
    def generate_full_journal(numbers: List[int], conn=None) -> Dict[str, Any]:
        """Génère le journal complet pour un tirage avec toutes les combinaisons"""
        
        # Générer toutes les combinaisons 2 à 2
        combos = list(combinations(numbers, 2))
        
        journal_entries = []
        errors = []
        
        # Utiliser la connexion fournie ou en créer une nouvelle
        internal_conn = False
        if conn is None:
            conn = JournalServiceV2._get_connection()
            internal_conn = True
            
        try:
            for num1, num2 in combos:
                entry = JournalServiceV2.generate_journal_entry(num1, num2, conn=conn)
                
                # On inclut tout dans journal_entries pour le frontend
                journal_entries.append(entry)
                
                if "error" in entry:
                    errors.append(entry)
        finally:
            if internal_conn:
                conn.close()
        
        # Analyser par univers
        by_universe = {}
        for entry in journal_entries:
            univers = entry.get("univers", "N/A")
            if univers not in by_universe:
                by_universe[univers] = []
            by_universe[univers].append(entry)
        
        # Analyser par caractère (seulement les entrées valides)
        valid_entries = [e for e in journal_entries if "error" not in e]
        character_analysis = JournalServiceV2._analyze_by_characters(valid_entries)
        
        return {
            "input_numbers": numbers,
            "total_combinations": len(combos),
            "valid_entries": len(journal_entries),
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
            "denomination": {},
            "engine": {},
            "beastie": {},
            "chip": {},
            "drawer": {}
        }
        
        for entry in journal_entries:
            # Tome
            tome = entry.get("tome")
            if tome:
                if tome not in analysis["tome"]:
                    analysis["tome"][tome] = {"count": 0, "combinations": []}
                analysis["tome"][tome]["count"] += 1
                analysis["tome"][tome]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Forme
            forme = entry.get("forme")
            if forme:
                if forme not in analysis["forme"]:
                    analysis["forme"][forme] = {"count": 0, "combinations": []}
                analysis["forme"][forme]["count"] += 1
                analysis["forme"][forme]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Granque
            granque = entry.get("granque_name")
            if granque:
                if granque not in analysis["granque"]:
                    analysis["granque"][granque] = {"count": 0, "combinations": []}
                analysis["granque"][granque]["count"] += 1
                analysis["granque"][granque]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Petique
            petique = entry.get("petique")
            if petique:
                if petique not in analysis["petique"]:
                    analysis["petique"][petique] = {"count": 0, "combinations": []}
                analysis["petique"][petique]["count"] += 1
                analysis["petique"][petique]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Univers
            univers = entry.get("univers")
            if univers:
                if univers not in analysis["univers"]:
                    analysis["univers"][univers] = {"count": 0, "combinations": []}
                analysis["univers"][univers]["count"] += 1
                analysis["univers"][univers]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Denomination
            denomination = entry.get("denomination")
            if denomination:
                if denomination not in analysis["denomination"]:
                    analysis["denomination"][denomination] = {"count": 0, "combinations": []}
                analysis["denomination"][denomination]["count"] += 1
                analysis["denomination"][denomination]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Engine
            engine = entry.get("engine")
            if engine:
                if engine not in analysis["engine"]:
                    analysis["engine"][engine] = {"count": 0, "combinations": []}
                analysis["engine"][engine]["count"] += 1
                analysis["engine"][engine]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Beastie
            beastie = entry.get("beastie")
            if beastie:
                if beastie not in analysis["beastie"]:
                    analysis["beastie"][beastie] = {"count": 0, "combinations": []}
                analysis["beastie"][beastie]["count"] += 1
                analysis["beastie"][beastie]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Chip
            chip = entry.get("chip")
            if chip:
                if chip not in analysis["chip"]:
                    analysis["chip"][chip] = {"count": 0, "combinations": []}
                analysis["chip"][chip]["count"] += 1
                analysis["chip"][chip]["combinations"].append([entry.get("num1"), entry.get("num2")])
            
            # Drawer
            drawer = entry.get("drawer")
            if drawer:
                if drawer not in analysis["drawer"]:
                    analysis["drawer"][drawer] = {"count": 0, "combinations": []}
                analysis["drawer"][drawer]["count"] += 1
                analysis["drawer"][drawer]["combinations"].append([entry.get("num1"), entry.get("num2")])
        
        return analysis
    
    @staticmethod
    def validate_draw_universe(numbers: List[int], expected_universe: str) -> Dict[str, Any]:
        """Valide que toutes les combinaisons d'un tirage appartiennent à l'univers attendu"""
        
        journal = JournalServiceV2.generate_full_journal(numbers)
        
        # Vérifier les univers
        invalid_combinations = []
        for entry in journal["journal_entries"]:
            if entry.get("univers") != expected_universe:
                invalid_combinations.append({
                    "combination": [entry.get("num1"), entry.get("num2")],
                    "expected_universe": expected_universe,
                    "actual_universe": entry.get("univers")
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
