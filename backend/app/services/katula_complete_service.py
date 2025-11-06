"""
Service Katula Complet
Intègre tous les éléments : matrice 8x6, granque, tomes, petiques, quadrants, filtres
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

class KatulaCompleteService:
    """Service complet pour la Table de Katula avec tous les éléments"""
    
    # Configuration matrice
    MATRIX_ROWS = 8
    MATRIX_COLS = 6
    TOTAL_CHIPS = 48
    
    # Configuration des univers
    UNIVERSES = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    # Configuration des tomes
    TOMES = ['tome1', 'tome2', 'tome3', 'tome4', 'tome5']
    
    # Configuration des granques
    GRANQUES = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta']
    
    # Configuration des petiques (quadrants)
    PETIQUES = ['q1', 'q2', 'q3', 'q4']
    
    @staticmethod
    def create_complete_katula_table(universe: str = "mundo") -> Dict[str, Any]:
        """Crée la table Katula complète avec tous les éléments"""
        
        table = {
            "universe": universe,
            "name": f"table_de_katula_{universe}",
            "dimensions": {
                "rows": KatulaCompleteService.MATRIX_ROWS,
                "columns": KatulaCompleteService.MATRIX_COLS,
                "total_chips": KatulaCompleteService.TOTAL_CHIPS
            },
            "matrix": [],
            "chip_positions": {},
            "side_panel": KatulaCompleteService._create_side_panel(),
            "filters": KatulaCompleteService._create_filters(),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "universe": universe,
                "version": "complete_v1.0"
            }
        }
        
        # Créer la matrice 8x6 avec tous les attributs
        chip_counter = 1
        for row in range(1, KatulaCompleteService.MATRIX_ROWS + 1):
            matrix_row = []
            for col in range(1, KatulaCompleteService.MATRIX_COLS + 1):
                chip_id = f"chip{chip_counter}"
                
                cell = {
                    "chip_id": chip_id,
                    "chip_number": chip_counter,
                    "row": row,
                    "column": col,
                    "position": f"R{row}C{col}",
                    "ligne": f"L{row}",
                    "colonne": f"C{col}",
                    "petique": KatulaCompleteService._get_petique(chip_counter),
                    "quadrant": KatulaCompleteService._get_quadrant(row, col),
                    "geometric_zone": KatulaCompleteService._get_geometric_zone(row, col),
                    "granque_name": KatulaCompleteService._get_granque_name(chip_counter),
                    "tome": KatulaCompleteService._get_tome(chip_counter),
                    "diagonal": KatulaCompleteService._get_diagonal_info(row, col),
                    "edge_info": KatulaCompleteService._get_edge_info(row, col),
                    "formes": KatulaCompleteService._get_chip_formes(universe, chip_counter),
                    "denominations": []
                }
                
                matrix_row.append(cell)
                table["chip_positions"][chip_id] = cell
                chip_counter += 1
            
            table["matrix"].append(matrix_row)
        
        return table
    
    @staticmethod
    def _create_side_panel() -> Dict[str, Any]:
        """Crée le side-panel avec tous les filtres"""
        return {
            "filters": {
                "granque": {
                    "label": "Granque",
                    "type": "select",
                    "options": KatulaCompleteService.GRANQUES,
                    "multiple": True
                },
                "tome": {
                    "label": "Tome",
                    "type": "select", 
                    "options": KatulaCompleteService.TOMES,
                    "multiple": True
                },
                "petique": {
                    "label": "Petique (Quadrant)",
                    "type": "select",
                    "options": KatulaCompleteService.PETIQUES,
                    "multiple": True
                },
                "quadrant": {
                    "label": "Quadrant Géométrique",
                    "type": "select",
                    "options": ["Q1_top_left", "Q2_top_right", "Q3_bottom_left", "Q4_bottom_right"],
                    "multiple": True
                },
                "zone": {
                    "label": "Zone Géométrique",
                    "type": "select",
                    "options": ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"],
                    "multiple": True
                },
                "ligne": {
                    "label": "Ligne",
                    "type": "range",
                    "min": 1,
                    "max": 8
                },
                "colonne": {
                    "label": "Colonne", 
                    "type": "range",
                    "min": 1,
                    "max": 6
                }
            },
            "actions": {
                "apply_filters": "Appliquer les filtres",
                "reset_filters": "Réinitialiser",
                "export_filtered": "Exporter la sélection"
            }
        }
    
    @staticmethod
    def _create_filters() -> Dict[str, Any]:
        """Crée la configuration des filtres"""
        return {
            "available_filters": [
                "granque", "tome", "petique", "quadrant", "zone", "ligne", "colonne", "forme"
            ],
            "filter_combinations": {
                "granque_tome": "Filtrer par Granque ET Tome",
                "petique_zone": "Filtrer par Petique ET Zone",
                "quadrant_ligne": "Filtrer par Quadrant ET Ligne"
            },
            "quick_filters": {
                "corners": "Coins de la matrice",
                "edges": "Bords de la matrice", 
                "center": "Centre de la matrice",
                "diagonals": "Diagonales"
            }
        }
    
    @staticmethod
    def _get_petique(chip_number: int) -> str:
        """Détermine la petique (quadrant) basée sur le numéro de chip"""
        if chip_number <= 12:
            return "q1"
        elif chip_number <= 24:
            return "q2"
        elif chip_number <= 36:
            return "q3"
        else:
            return "q4"
    
    @staticmethod
    def _get_granque_name(chip_number: int) -> str:
        """Génère un nom de granque basé sur le chip"""
        granque_base = KatulaCompleteService.GRANQUES[chip_number % len(KatulaCompleteService.GRANQUES)]
        return f"{granque_base}-{chip_number}"
    
    @staticmethod
    def _get_tome(chip_number: int) -> str:
        """Détermine le tome basé sur le chip"""
        return KatulaCompleteService.TOMES[chip_number % len(KatulaCompleteService.TOMES)]
    
    @staticmethod
    def _get_quadrant(row: int, col: int) -> str:
        """Détermine le quadrant géométrique"""
        if row <= 4 and col <= 3:
            return "Q1_top_left"
        elif row <= 4 and col > 3:
            return "Q2_top_right"
        elif row > 4 and col <= 3:
            return "Q3_bottom_left"
        else:
            return "Q4_bottom_right"
    
    @staticmethod
    def _get_geometric_zone(row: int, col: int) -> str:
        """Détermine la zone géométrique"""
        if row <= 2:
            vertical = "top"
        elif row <= 6:
            vertical = "middle"
        else:
            vertical = "bottom"
        
        if col <= 2:
            horizontal = "left"
        elif col <= 4:
            horizontal = "center"
        else:
            horizontal = "right"
        
        return f"{vertical}_{horizontal}"
    
    @staticmethod
    def _get_diagonal_info(row: int, col: int) -> Dict[str, Any]:
        """Calcule les informations diagonales"""
        return {
            "on_main_diagonal": (row - col) == -2,
            "on_anti_diagonal": (row + col) == 7,
            "diagonal_sum": row + col,
            "diagonal_diff": row - col
        }
    
    @staticmethod
    def _get_edge_info(row: int, col: int) -> Dict[str, Any]:
        """Détermine les informations de bord"""
        is_top = row == 1
        is_bottom = row == KatulaCompleteService.MATRIX_ROWS
        is_left = col == 1
        is_right = col == KatulaCompleteService.MATRIX_COLS
        
        is_corner = (is_top or is_bottom) and (is_left or is_right)
        is_edge = is_top or is_bottom or is_left or is_right
        
        return {
            "is_corner": is_corner,
            "is_edge": is_edge,
            "is_center": not is_edge,
            "edge_type": KatulaCompleteService._get_edge_type(row, col)
        }
    
    @staticmethod
    def _get_edge_type(row: int, col: int) -> str:
        """Détermine le type de bord"""
        if row == 1 and col == 1:
            return "top_left_corner"
        elif row == 1 and col == KatulaCompleteService.MATRIX_COLS:
            return "top_right_corner"
        elif row == KatulaCompleteService.MATRIX_ROWS and col == 1:
            return "bottom_left_corner"
        elif row == KatulaCompleteService.MATRIX_ROWS and col == KatulaCompleteService.MATRIX_COLS:
            return "bottom_right_corner"
        elif row == 1:
            return "top_edge"
        elif row == KatulaCompleteService.MATRIX_ROWS:
            return "bottom_edge"
        elif col == 1:
            return "left_edge"
        elif col == KatulaCompleteService.MATRIX_COLS:
            return "right_edge"
        else:
            return "center"
    
    @staticmethod
    def _get_chip_formes(universe: str, chip_number: int) -> List[str]:
        """Détermine les formes pour un chip selon l'univers"""
        if universe in ['mundo', 'fruity']:
            return ['carre', 'triangle', 'cercle', 'rectangle']
        else:
            # Univers avec formes composites
            base_formes = ['carre', 'triangle', 'cercle', 'rectangle']
            composite_formes = [
                'carre-triangle', 'carre-cercle', 'carre-rectangle',
                'triangle-cercle', 'triangle-rectangle', 'cercle-rectangle'
            ]
            return base_formes + composite_formes
    
    @staticmethod
    def apply_filters(table_data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les filtres à la table Katula"""
        filtered_chips = []
        
        for chip_id, chip_data in table_data["chip_positions"].items():
            include_chip = True
            
            # Filtrer par granque
            if "granque" in filters and filters["granque"]:
                if chip_data["granque_name"].split('-')[0] not in filters["granque"]:
                    include_chip = False
            
            # Filtrer par tome
            if "tome" in filters and filters["tome"]:
                if chip_data["tome"] not in filters["tome"]:
                    include_chip = False
            
            # Filtrer par petique
            if "petique" in filters and filters["petique"]:
                if chip_data["petique"] not in filters["petique"]:
                    include_chip = False
            
            # Filtrer par quadrant
            if "quadrant" in filters and filters["quadrant"]:
                if chip_data["quadrant"] not in filters["quadrant"]:
                    include_chip = False
            
            # Filtrer par zone
            if "zone" in filters and filters["zone"]:
                if chip_data["geometric_zone"] not in filters["zone"]:
                    include_chip = False
            
            # Filtrer par ligne
            if "ligne" in filters and filters["ligne"]:
                ligne_range = filters["ligne"]
                if not (ligne_range["min"] <= chip_data["row"] <= ligne_range["max"]):
                    include_chip = False
            
            # Filtrer par colonne
            if "colonne" in filters and filters["colonne"]:
                col_range = filters["colonne"]
                if not (col_range["min"] <= chip_data["column"] <= col_range["max"]):
                    include_chip = False
            
            if include_chip:
                filtered_chips.append(chip_data)
        
        return {
            "filtered_chips": filtered_chips,
            "total_filtered": len(filtered_chips),
            "total_original": len(table_data["chip_positions"]),
            "filters_applied": filters,
            "filter_timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_side_panel_data(universe: str) -> Dict[str, Any]:
        """Retourne les données pour le side-panel"""
        return {
            "universe": universe,
            "available_granques": KatulaCompleteService.GRANQUES,
            "available_tomes": KatulaCompleteService.TOMES,
            "available_petiques": KatulaCompleteService.PETIQUES,
            "available_quadrants": ["Q1_top_left", "Q2_top_right", "Q3_bottom_left", "Q4_bottom_right"],
            "available_zones": [
                "top_left", "top_center", "top_right",
                "middle_left", "middle_center", "middle_right", 
                "bottom_left", "bottom_center", "bottom_right"
            ],
            "quick_filters": {
                "corners": [1, 6, 43, 48],
                "edges": list(range(1, 7)) + list(range(43, 49)) + [7, 12, 13, 18, 19, 24, 25, 30, 31, 36, 37, 42],
                "center": [20, 21, 26, 27],
                "diagonals": [1, 8, 15, 22, 29, 36, 6, 11, 16, 21, 26, 31]
            }
        }