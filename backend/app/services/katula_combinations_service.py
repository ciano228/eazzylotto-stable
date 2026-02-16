"""
Service Table de Katula basé sur la table 'combinations'
Logique métier originale utilisant les vraies données PostgreSQL
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

class KatulaCombinationsService:
    """
    Service pour la table de Katula basé sur la table 'combinations'
    Utilise la vraie logique métier avec chip, forme, denomination
    """
    
    # Ordre des tiroirs par univers (logique métier originale)
    DRAWER_ORDER = {
        "mundo": ["carre", "triangle", "cercle", "rectangle"],
        "roaster": ["carre", "triangle", "cercle", "rectangle"], 
        "trigga": ["carre", "triangle", "cercle", "rectangle"],
        "sunshine": ["carre", "triangle", "cercle", "rectangle"],
        "fruity": ["carre", "triangle", "cercle", "rectangle"]
    }
    
    # Icônes par forme
    FORME_ICONS = {
        "carre": "⬜",
        "triangle": "🔺",
        "cercle": "🔵", 
        "rectangle": "▬"
    }
    
    # Couleurs par forme
    FORME_COLORS = {
        "carre": "#ffeb3b",
        "triangle": "#ff9800",
        "cercle": "#4caf50", 
        "rectangle": "#2196f3"
    }
    
    @staticmethod
    def get_katula_table_from_combinations(
        db: Session,
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """
        Récupère la table de Katula depuis la table 'combinations'
        Structure: 8x6 = 48 chips avec tiroirs par forme
        """
        try:
            # Récupérer les données depuis la table combinations
            raw_data = KatulaCombinationsService._get_combinations_data(db, universe)
            
            if "error" in raw_data:
                return raw_data
            
            # Créer la structure 8x6
            table_structure = KatulaCombinationsService._create_table_structure(universe)
            
            # Remplir avec les données combinations
            populated_table = KatulaCombinationsService._populate_table_with_combinations(
                table_structure, raw_data, universe
            )
            
            return populated_table
            
        except Exception as e:
            return {"error": f"Erreur lors de la création de la table: {str(e)}"}
    
    @staticmethod
    def _get_combinations_data(db: Session, universe: str) -> Dict[str, Any]:
        """Récupère les données depuis la table combinations"""
        
        try:
            # Requête sur la table combinations
            query = """
                SELECT 
                    chip,
                    ligne,
                    colonne,
                    forme,
                    denomination,
                    tome,
                    granque_name,
                    petique,
                    COUNT(*) as frequency
                FROM combinations
                WHERE univers = :universe 
                AND chip IS NOT NULL 
                AND forme IS NOT NULL
                GROUP BY chip, ligne, colonne, forme, denomination, tome, granque_name, petique
                ORDER BY chip, forme, denomination
            """
            
            result = db.execute(text(query), {"universe": universe})
            rows = result.fetchall()
            
            # Organiser par chip et forme
            chips_data = {}
            for row in rows:
                chip = row.chip
                ligne = row.ligne
                colonne = row.colonne
                forme = row.forme
                denomination = row.denomination
                tome = row.tome
                granque_name = row.granque_name
                petique = row.petique
                frequency = row.frequency
                
                # Extraire le numéro du chip (ex: "chip1" -> 1)
                try:
                    if isinstance(chip, str) and chip.startswith('chip'):
                        chip_num = int(chip.replace('chip', ''))
                    else:
                        chip_num = int(chip)
                except:
                    continue  # Ignorer les chips invalides
                
                if chip_num not in chips_data:
                    chips_data[chip_num] = {
                        "ligne": ligne,
                        "colonne": colonne,
                        "formes": {}
                    }
                
                if forme not in chips_data[chip_num]["formes"]:
                    chips_data[chip_num]["formes"][forme] = []
                
                chips_data[chip_num]["formes"][forme].append({
                    "denomination": denomination,
                    "tome": tome,
                    "granque_name": granque_name,
                    "petique": petique,
                    "frequency": frequency
                })
            
            return {
                "chips": chips_data,
                "total_entries": len(rows),
                "universe": universe,
                "source": "combinations_table"
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des données combinations: {str(e)}"}
    
    @staticmethod
    def _create_table_structure(universe: str) -> Dict[str, Any]:
        """Crée la structure de base 8x6"""
        
        table = {
            "universe": universe,
            "dimensions": {"rows": 8, "columns": 6, "total_chips": 48},
            "drawer_order": KatulaCombinationsService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"]),
            "matrix": [],
            "chips": {}
        }
        
        # Créer la matrice 8x6
        chip_counter = 1
        for row in range(1, 9):  # 8 lignes
            matrix_row = []
            for col in range(1, 7):  # 6 colonnes
                chip_info = {
                    "chip_name": f"chip{chip_counter}",
                    "chip_number": chip_counter,
                    "position": f"L{row}C{col}",
                    "row": row,
                    "column": col,
                    "drawers": {}
                }
                
                # Initialiser les tiroirs selon l'ordre
                for drawer_name in table["drawer_order"]:
                    chip_info["drawers"][drawer_name] = {
                        "forme": drawer_name,
                        "icon": KatulaCombinationsService.FORME_ICONS.get(drawer_name, "⬜"),
                        "color": KatulaCombinationsService.FORME_COLORS.get(drawer_name, "#cccccc"),
                        "denominations": []
                    }
                
                matrix_row.append(chip_info)
                table["chips"][f"chip{chip_counter}"] = chip_info
                chip_counter += 1
            
            table["matrix"].append(matrix_row)
        
        return table
    
    @staticmethod
    def _populate_table_with_combinations(
        table_structure: Dict[str, Any],
        combinations_data: Dict[str, Any],
        universe: str
    ) -> Dict[str, Any]:
        """Remplit la table avec les données de combinations"""
        
        if "error" in combinations_data:
            table_structure["data_status"] = "error"
            table_structure["error"] = combinations_data["error"]
            return table_structure
        
        chips_data = combinations_data.get("chips", {})
        
        # Remplir chaque chip
        for chip_name, chip_info in table_structure["chips"].items():
            chip_number = chip_info["chip_number"]
            
            if chip_number in chips_data:
                chip_data = chips_data[chip_number]
                
                # Vérifier la cohérence position BD vs calculée
                if "ligne" in chip_data and "colonne" in chip_data:
                    bd_position = f"L{chip_data['ligne']}C{chip_data['colonne']}"
                    if bd_position != chip_info["position"]:
                        chip_info["position_note"] = f"BD: {bd_position}, Calculé: {chip_info['position']}"
                
                # Remplir les tiroirs avec les dénominations
                for forme, forme_data in chip_data.get("formes", {}).items():
                    if forme in chip_info["drawers"]:
                        # Grouper les dénominations
                        denominations_list = []
                        for item in forme_data:
                            denominations_list.append({
                                "text": item["denomination"],
                                "tome": item["tome"],
                                "granque_name": item["granque_name"],
                                "petique": item["petique"],
                                "frequency": item["frequency"]
                            })
                        
                        chip_info["drawers"][forme]["denominations"] = denominations_list
                        
                        # Créer le texte d'affichage avec séparateur "/"
                        if denominations_list:
                            display_text = " / ".join([d["text"] for d in denominations_list])
                            chip_info["drawers"][forme]["display_text"] = display_text
                            chip_info["drawers"][forme]["has_data"] = True
                        else:
                            chip_info["drawers"][forme]["display_text"] = ""
                            chip_info["drawers"][forme]["has_data"] = False
        
        # Mettre à jour la matrice
        for row_idx, row in enumerate(table_structure["matrix"]):
            for col_idx, cell in enumerate(row):
                chip_name = cell["chip_name"]
                if chip_name in table_structure["chips"]:
                    table_structure["matrix"][row_idx][col_idx] = table_structure["chips"][chip_name]
        
        # Métadonnées
        table_structure["data_status"] = "loaded"
        table_structure["data_source"] = "combinations_table"
        table_structure["total_data_entries"] = combinations_data.get("total_entries", 0)
        table_structure["last_updated"] = datetime.now().isoformat()
        
        return table_structure
    
    @staticmethod
    def get_chip_from_combinations(
        db: Session,
        universe: str,
        chip_number: int
    ) -> Dict[str, Any]:
        """Récupère les données d'un chip depuis combinations"""
        
        if chip_number < 1 or chip_number > 48:
            return {"error": "Numéro de chip invalide (1-48)"}
        
        try:
            # Requête pour le chip spécifique
            query = """
                SELECT 
                    ligne,
                    colonne,
                    forme,
                    denomination,
                    tome,
                    granque_name,
                    petique,
                    COUNT(*) as frequency
                FROM combinations
                WHERE univers = :universe 
                AND (chip = :chip_str OR chip = :chip_num)
                GROUP BY ligne, colonne, forme, denomination, tome, granque_name, petique
                ORDER BY forme, denomination
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "chip_str": f"chip{chip_number}",
                "chip_num": chip_number
            })
            rows = result.fetchall()
            
            if not rows:
                return {"error": f"Aucune donnée trouvée pour chip{chip_number} dans {universe}"}
            
            # Organiser les données
            chip_data = {
                "chip_name": f"chip{chip_number}",
                "chip_number": chip_number,
                "universe": universe,
                "drawers": {}
            }
            
            # Position depuis la BD
            first_row = rows[0]
            chip_data["position_bd"] = f"L{first_row.ligne}C{first_row.colonne}"
            chip_data["position_calculated"] = f"L{((chip_number - 1) // 6) + 1}C{((chip_number - 1) % 6) + 1}"
            
            # Ordre des tiroirs
            drawer_order = KatulaCombinationsService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"])
            
            # Organiser par forme
            formes_data = {}
            for row in rows:
                forme = row.forme
                if forme not in formes_data:
                    formes_data[forme] = []
                
                formes_data[forme].append({
                    "denomination": row.denomination,
                    "tome": row.tome,
                    "granque_name": row.granque_name,
                    "petique": row.petique,
                    "frequency": row.frequency
                })
            
            # Créer les tiroirs dans l'ordre
            for drawer_name in drawer_order:
                drawer_info = {
                    "forme": drawer_name,
                    "icon": KatulaCombinationsService.FORME_ICONS.get(drawer_name, "⬜"),
                    "color": KatulaCombinationsService.FORME_COLORS.get(drawer_name, "#cccccc"),
                    "denominations": formes_data.get(drawer_name, []),
                    "has_data": drawer_name in formes_data
                }
                
                # Texte d'affichage
                if drawer_info["has_data"]:
                    display_text = " / ".join([d["denomination"] for d in drawer_info["denominations"]])
                    drawer_info["display_text"] = display_text
                    drawer_info["formatted_display"] = f"{drawer_info['icon']} {display_text}"
                else:
                    drawer_info["display_text"] = ""
                    drawer_info["formatted_display"] = f"{drawer_info['icon']} (vide)"
                
                chip_data["drawers"][drawer_name] = drawer_info
            
            return chip_data
            
        except Exception as e:
            return {"error": f"Erreur lors de la récupération du chip: {str(e)}"}
    
    @staticmethod
    def get_combinations_by_denomination(
        db: Session,
        universe: str,
        denomination: str
    ) -> List[Dict[str, Any]]:
        """Récupère toutes les combinaisons pour une dénomination"""
        
        try:
            query = """
                SELECT 
                    combination_id,
                    num1,
                    num2,
                    chip,
                    forme,
                    denomination,
                    alpha_ranking,
                    tome,
                    granque_name,
                    petique
                FROM combinations
                WHERE univers = :universe AND denomination = :denomination
                ORDER BY alpha_ranking, num1, num2
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "denomination": denomination
            })
            rows = result.fetchall()
            
            combinations = []
            for row in rows:
                combinations.append({
                    "combination_id": row.combination_id,
                    "num1": row.num1,
                    "num2": row.num2,
                    "combination": f"{row.num1}-{row.num2}",
                    "chip": row.chip,
                    "forme": row.forme,
                    "denomination": row.denomination,
                    "alpha_ranking": row.alpha_ranking,
                    "tome": row.tome,
                    "granque_name": row.granque_name,
                    "petique": row.petique
                })
            
            return combinations
            
        except Exception as e:
            return [{"error": f"Erreur lors de la récupération des combinaisons: {str(e)}"}]