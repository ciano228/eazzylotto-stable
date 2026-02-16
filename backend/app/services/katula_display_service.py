"""
Service d'Affichage Table de Katula
Gère l'affichage des chips avec icônes et dénominations selon la logique métier
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

class KatulaDisplayService:
    """
    Service pour l'affichage formaté de la table de Katula
    Chaque chip avec nom, tiroirs avec icônes et dénominations
    """
    
    # Configuration des icônes par forme
    FORME_ICONS = {
        "carre": "⬜",
        "triangle": "🔺", 
        "cercle": "🔵",
        "rectangle": "▬",
        "road": "🛣️",
        "fire": "🔥",
        "shoes": "👟",
        "bottle": "🍾"
    }
    
    # Couleurs CSS par forme
    FORME_COLORS = {
        "carre": "#ffeb3b",
        "triangle": "#ff9800", 
        "cercle": "#4caf50",
        "rectangle": "#2196f3",
        "road": "#795548",
        "fire": "#f44336",
        "shoes": "#9c27b0",
        "bottle": "#00bcd4"
    }
    
    # Ordre des tiroirs par univers
    DRAWER_ORDER = {
        "mundo": ["carre", "triangle", "cercle", "rectangle"],
        "roaster": ["carre", "triangle", "cercle", "rectangle"],
        "trigga": ["carre", "triangle", "cercle", "rectangle"],
        "sunshine": ["carre", "triangle", "cercle", "rectangle"],
        "fruity": ["road", "fire", "shoes", "bottle"]
    }
    
    @staticmethod
    def get_formatted_katula_table(
        db: Session, 
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """
        Récupère la table de Katula formatée pour l'affichage
        Avec chips nommés, icônes et dénominations
        """
        try:
            # Récupérer les données brutes
            raw_data = KatulaDisplayService._get_raw_chip_data(db, universe)
            
            if "error" in raw_data:
                return raw_data
            
            # Créer la structure de la table 8x6
            formatted_table = KatulaDisplayService._create_formatted_structure(universe)
            
            # Remplir avec les données réelles
            populated_table = KatulaDisplayService._populate_with_data(
                formatted_table, raw_data, universe
            )
            
            return populated_table
            
        except Exception as e:
            return {"error": f"Erreur lors du formatage de la table: {str(e)}"}
    
    @staticmethod
    def _get_raw_chip_data(db: Session, universe: str) -> Dict[str, Any]:
        """Récupère les données brutes depuis PostgreSQL"""
        
        try:
            # Requête pour récupérer toutes les données par chip
            query = f"""
                SELECT 
                    chip,
                    ligne,
                    colonne,
                    forme,
                    denomination,
                    COUNT(*) as frequency
                FROM {universe}
                WHERE chip BETWEEN 1 AND 48
                GROUP BY chip, ligne, colonne, forme, denomination
                ORDER BY chip, forme, denomination
            """
            
            result = db.execute(text(query))
            rows = result.fetchall()
            
            # Organiser les données par chip
            chips_data = {}
            for row in rows:
                chip_num = row.chip
                ligne = row.ligne
                colonne = row.colonne
                forme = row.forme
                denomination = row.denomination
                frequency = row.frequency
                
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
                    "frequency": frequency
                })
            
            return {
                "chips": chips_data,
                "total_entries": len(rows),
                "universe": universe
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des données: {str(e)}"}
    
    @staticmethod
    def _create_formatted_structure(universe: str) -> Dict[str, Any]:
        """Crée la structure formatée de base"""
        
        table = {
            "universe": universe,
            "dimensions": {"rows": 8, "columns": 6, "total_chips": 48},
            "drawer_order": KatulaDisplayService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"]),
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
                        "icon": KatulaDisplayService.FORME_ICONS.get(drawer_name, "⬜"),
                        "color": KatulaDisplayService.FORME_COLORS.get(drawer_name, "#cccccc"),
                        "denominations": []
                    }
                
                matrix_row.append(chip_info)
                table["chips"][f"chip{chip_counter}"] = chip_info
                chip_counter += 1
            
            table["matrix"].append(matrix_row)
        
        return table
    
    @staticmethod
    def _populate_with_data(
        formatted_table: Dict[str, Any], 
        raw_data: Dict[str, Any], 
        universe: str
    ) -> Dict[str, Any]:
        """Remplit la structure avec les données réelles"""
        
        if "error" in raw_data:
            formatted_table["data_status"] = "error"
            formatted_table["error"] = raw_data["error"]
            return formatted_table
        
        chips_data = raw_data.get("chips", {})
        
        # Remplir chaque chip avec ses données
        for chip_name, chip_info in formatted_table["chips"].items():
            chip_number = chip_info["chip_number"]
            
            if chip_number in chips_data:
                chip_data = chips_data[chip_number]
                
                # Mettre à jour la position si disponible
                if "ligne" in chip_data and "colonne" in chip_data:
                    expected_position = f"L{chip_data['ligne']}C{chip_data['colonne']}"
                    if expected_position != chip_info["position"]:
                        chip_info["position_note"] = f"BD: {expected_position}, Calculé: {chip_info['position']}"
                
                # Remplir les tiroirs avec les dénominations
                for forme, forme_data in chip_data.get("formes", {}).items():
                    if forme in chip_info["drawers"]:
                        # Grouper les dénominations avec séparateur "/"
                        denominations_list = []
                        for item in forme_data:
                            denominations_list.append({
                                "text": item["denomination"],
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
                    else:
                        # Forme non prévue dans l'ordre des tiroirs
                        chip_info["drawers"][forme] = {
                            "forme": forme,
                            "icon": KatulaDisplayService.FORME_ICONS.get(forme, "❓"),
                            "color": KatulaDisplayService.FORME_COLORS.get(forme, "#cccccc"),
                            "denominations": forme_data,
                            "display_text": " / ".join([item["denomination"] for item in forme_data]),
                            "has_data": True,
                            "unexpected": True
                        }
        
        # Mettre à jour la matrice avec les données remplies
        for row_idx, row in enumerate(formatted_table["matrix"]):
            for col_idx, cell in enumerate(row):
                chip_name = cell["chip_name"]
                if chip_name in formatted_table["chips"]:
                    formatted_table["matrix"][row_idx][col_idx] = formatted_table["chips"][chip_name]
        
        # Ajouter les métadonnées
        formatted_table["data_status"] = "loaded"
        formatted_table["total_data_entries"] = raw_data.get("total_entries", 0)
        formatted_table["last_updated"] = datetime.now().isoformat()
        
        return formatted_table
    
    @staticmethod
    def get_chip_display_data(
        db: Session, 
        universe: str, 
        chip_number: int
    ) -> Dict[str, Any]:
        """
        Récupère les données d'affichage pour un chip spécifique
        Format: chip1 avec tiroirs icône + dénomination
        """
        
        if chip_number < 1 or chip_number > 48:
            return {"error": "Numéro de chip invalide (1-48)"}
        
        try:
            # Récupérer les données du chip
            query = f"""
                SELECT 
                    ligne,
                    colonne,
                    forme,
                    denomination,
                    COUNT(*) as frequency
                FROM {universe}
                WHERE chip = :chip_number
                GROUP BY ligne, colonne, forme, denomination
                ORDER BY forme, denomination
            """
            
            result = db.execute(text(query), {"chip_number": chip_number})
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
            
            # Position depuis la BD (première ligne)
            first_row = rows[0]
            chip_data["position_bd"] = f"L{first_row.ligne}C{first_row.colonne}"
            chip_data["position_calculated"] = f"L{((chip_number - 1) // 6) + 1}C{((chip_number - 1) % 6) + 1}"
            
            # Ordre des tiroirs pour cet univers
            drawer_order = KatulaDisplayService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"])
            
            # Organiser par forme
            formes_data = {}
            for row in rows:
                forme = row.forme
                if forme not in formes_data:
                    formes_data[forme] = []
                
                formes_data[forme].append({
                    "denomination": row.denomination,
                    "frequency": row.frequency
                })
            
            # Créer les tiroirs dans l'ordre
            for drawer_name in drawer_order:
                drawer_info = {
                    "forme": drawer_name,
                    "icon": KatulaDisplayService.FORME_ICONS.get(drawer_name, "⬜"),
                    "color": KatulaDisplayService.FORME_COLORS.get(drawer_name, "#cccccc"),
                    "denominations": formes_data.get(drawer_name, []),
                    "has_data": drawer_name in formes_data
                }
                
                # Créer le texte d'affichage
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
            return {"error": f"Erreur lors de la récupération des données du chip: {str(e)}"}
    
    @staticmethod
    def generate_html_display(table_data: Dict[str, Any]) -> str:
        """Génère le HTML pour l'affichage de la table"""
        
        if "error" in table_data:
            return f"<div class='error'>Erreur: {table_data['error']}</div>"
        
        html = f"""
        <div class="katula-table-container">
            <div class="table-header">
                <h2>Table de Katula - {table_data['universe'].upper()}</h2>
                <p>Matrice {table_data['dimensions']['rows']}x{table_data['dimensions']['columns']} - {table_data['dimensions']['total_chips']} chips</p>
            </div>
            
            <div class="katula-grid">
        """
        
        # En-têtes des colonnes
        html += "<div class='grid-header'></div>"  # Coin vide
        for col in range(1, 7):
            html += f"<div class='grid-header'>C{col}</div>"
        
        # Lignes de la matrice
        for row_idx, row in enumerate(table_data["matrix"]):
            # En-tête de ligne
            html += f"<div class='ligne-label'>L{row_idx + 1}</div>"
            
            # Cellules de la ligne
            for cell in row:
                html += f"""
                <div class='chip-cell'>
                    <div class='chip-header'>{cell['chip_name']}</div>
                    <div class='chip-content'>
                """
                
                # Tiroirs du chip
                for drawer_name, drawer_info in cell["drawers"].items():
                    css_class = "chip-drawer"
                    if drawer_info.get("has_data", False):
                        css_class += " has-data"
                    
                    html += f"""
                    <div class='{css_class}' style='border-left: 3px solid {drawer_info["color"]}'>
                        <div class='drawer-content'>
                            <span class='drawer-icon'>{drawer_info["icon"]}</span>
                            <span class='drawer-text'>{drawer_info.get("display_text", "")}</span>
                        </div>
                    </div>
                    """
                
                html += """
                    </div>
                </div>
                """
        
        html += """
            </div>
        </div>
        """
        
        return html