"""
Service Intégré de Table de Katula
Combine la structure géométrique 8x6 avec les données PostgreSQL réelles
"""
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

class KatulaTableIntegratedService:
    """
    Service intégré pour la gestion complète de la Table de Katula
    Matrice géométrique 8x6 avec données PostgreSQL réelles
    """
    
    # Configuration de la matrice 8 lignes x 6 colonnes = 48 chips
    MATRIX_ROWS = 8
    MATRIX_COLS = 6
    TOTAL_CHIPS = 48
    
    # Ordre des tiroirs par univers (business logic)
    DRAWER_ORDER = {
        "mundo": ["carre", "triangle", "cercle", "rectangle"],
        "roaster": ["carre", "triangle", "cercle", "rectangle"],
        "trigga": ["carre", "triangle", "cercle", "rectangle"],
        "sunshine": ["carre", "triangle", "cercle", "rectangle"],
        "fruity": ["road", "fire", "shoes", "bottle"]
    }
    
    @staticmethod
    def get_complete_katula_table(
        db: Session, 
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """
        Récupère la table de Katula complète avec données PostgreSQL réelles
        """
        try:
            # Créer la structure de base
            katula_table = KatulaTableIntegratedService._create_base_structure(universe)
            
            # Charger les données réelles depuis PostgreSQL
            real_data = KatulaTableIntegratedService._load_real_data(db, universe)
            
            # Intégrer les données réelles dans la structure
            integrated_table = KatulaTableIntegratedService._integrate_real_data(
                katula_table, real_data, universe
            )
            
            return integrated_table
            
        except Exception as e:
            return {"error": f"Erreur lors de la création de la table: {str(e)}"}
    @staticmethod
    def _create_base_structure(universe: str) -> Dict[str, Any]:
        """Crée la structure de base de la table de Katula"""
        
        table = {
            "universe": universe,
            "name": f"table_de_katula_{universe}",
            "dimensions": {
                "rows": KatulaTableIntegratedService.MATRIX_ROWS,
                "columns": KatulaTableIntegratedService.MATRIX_COLS,
                "total_chips": KatulaTableIntegratedService.TOTAL_CHIPS
            },
            "matrix": [],
            "chip_positions": {},
            "drawer_order": KatulaTableIntegratedService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"])
        }
        
        # Créer la matrice 8x6
        chip_counter = 1
        for row in range(1, KatulaTableIntegratedService.MATRIX_ROWS + 1):
            matrix_row = []
            for col in range(1, KatulaTableIntegratedService.MATRIX_COLS + 1):
                chip_id = f"chip{chip_counter}"
                
                cell = {
                    "chip_id": chip_id,
                    "chip_number": chip_counter,
                    "row": row,
                    "column": col,
                    "position": f"R{row}C{col}",
                    "drawers": {},  # Sera rempli avec les données réelles
                    "geometric_info": KatulaTableIntegratedService._get_geometric_info(row, col)
                }
                
                matrix_row.append(cell)
                table["chip_positions"][chip_id] = cell
                chip_counter += 1
            
            table["matrix"].append(matrix_row)
        
        return table
    
    @staticmethod
    def _load_real_data(db: Session, universe: str) -> Dict[str, Any]:
        """Charge les données réelles depuis PostgreSQL"""
        
        try:
            # Requête pour récupérer les données par chip
            query = f"""
                SELECT 
                    chip,
                    forme,
                    denomination,
                    COUNT(*) as frequency
                FROM {universe}
                WHERE chip BETWEEN 1 AND 48
                GROUP BY chip, forme, denomination
                ORDER BY chip, forme, denomination
            """
            
            result = db.execute(text(query))
            rows = result.fetchall()
            
            # Organiser les données par chip et forme
            chips_data = {}
            for row in rows:
                chip_num = row.chip
                forme = row.forme
                denomination = row.denomination
                frequency = row.frequency
                
                if chip_num not in chips_data:
                    chips_data[chip_num] = {}
                
                if forme not in chips_data[chip_num]:
                    chips_data[chip_num][forme] = []
                
                chips_data[chip_num][forme].append({
                    "denomination": denomination,
                    "frequency": frequency
                })
            
            return {
                "chips": chips_data,
                "total_entries": len(rows),
                "source": f"PostgreSQL table: {universe}"
            }
            
        except Exception as e:
            return {"error": f"Erreur lors du chargement des données: {str(e)}"}
    @staticmethod
    def _integrate_real_data(
        katula_table: Dict[str, Any], 
        real_data: Dict[str, Any], 
        universe: str
    ) -> Dict[str, Any]:
        """Intègre les données réelles dans la structure Katula"""
        
        if "error" in real_data:
            katula_table["data_status"] = "error"
            katula_table["error"] = real_data["error"]
            return katula_table
        
        drawer_order = KatulaTableIntegratedService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"])
        chips_data = real_data.get("chips", {})
        
        # Intégrer les données dans chaque chip
        for chip_id, chip_info in katula_table["chip_positions"].items():
            chip_number = chip_info["chip_number"]
            
            if chip_number in chips_data:
                # Organiser les tiroirs selon l'ordre défini
                for drawer_name in drawer_order:
                    if drawer_name in chips_data[chip_number]:
                        chip_info["drawers"][drawer_name] = chips_data[chip_number][drawer_name]
                    else:
                        chip_info["drawers"][drawer_name] = []
            else:
                # Chip sans données - créer structure vide
                for drawer_name in drawer_order:
                    chip_info["drawers"][drawer_name] = []
        
        # Mettre à jour la matrice avec les données intégrées
        for row_idx, row in enumerate(katula_table["matrix"]):
            for col_idx, cell in enumerate(row):
                chip_id = cell["chip_id"]
                if chip_id in katula_table["chip_positions"]:
                    katula_table["matrix"][row_idx][col_idx] = katula_table["chip_positions"][chip_id]
        
        # Ajouter les métadonnées
        katula_table["data_status"] = "loaded"
        katula_table["data_source"] = real_data.get("source", "PostgreSQL")
        katula_table["total_data_entries"] = real_data.get("total_entries", 0)
        katula_table["last_updated"] = datetime.now().isoformat()
        
        return katula_table
    
    @staticmethod
    def _get_geometric_info(row: int, col: int) -> Dict[str, Any]:
        """Calcule les informations géométriques d'une position"""
        
        # Zone géométrique
        if row <= 2:
            vertical_zone = "top"
        elif row <= 6:
            vertical_zone = "middle"
        else:
            vertical_zone = "bottom"
        
        if col <= 2:
            horizontal_zone = "left"
        elif col <= 4:
            horizontal_zone = "center"
        else:
            horizontal_zone = "right"
        
        geometric_zone = f"{vertical_zone}_{horizontal_zone}"
        
        # Quadrant
        if row <= 4 and col <= 3:
            quadrant = "Q1_top_left"
        elif row <= 4 and col > 3:
            quadrant = "Q2_top_right"
        elif row > 4 and col <= 3:
            quadrant = "Q3_bottom_left"
        else:
            quadrant = "Q4_bottom_right"
        
        # Informations de bord
        is_top_edge = row == 1
        is_bottom_edge = row == KatulaTableIntegratedService.MATRIX_ROWS
        is_left_edge = col == 1
        is_right_edge = col == KatulaTableIntegratedService.MATRIX_COLS
        is_corner = (is_top_edge or is_bottom_edge) and (is_left_edge or is_right_edge)
        is_edge = is_top_edge or is_bottom_edge or is_left_edge or is_right_edge
        
        return {
            "geometric_zone": geometric_zone,
            "quadrant": quadrant,
            "is_corner": is_corner,
            "is_edge": is_edge,
            "is_center": not is_edge,
            "diagonal_sum": row + col,
            "diagonal_diff": row - col
        }
    
    @staticmethod
    def get_chip_data(
        db: Session, 
        universe: str, 
        chip_number: int
    ) -> Dict[str, Any]:
        """Récupère les données spécifiques d'un chip"""
        
        if chip_number < 1 or chip_number > 48:
            return {"error": "Numéro de chip invalide (1-48)"}
        
        try:
            query = f"""
                SELECT 
                    forme,
                    denomination,
                    COUNT(*) as frequency
                FROM {universe}
                WHERE chip = :chip_number
                GROUP BY forme, denomination
                ORDER BY forme, denomination
            """
            
            result = db.execute(text(query), {"chip_number": chip_number})
            rows = result.fetchall()
            
            drawer_order = KatulaTableIntegratedService.DRAWER_ORDER.get(universe, ["carre", "triangle", "cercle", "rectangle"])
            
            # Organiser par tiroirs
            drawers = {}
            for drawer_name in drawer_order:
                drawers[drawer_name] = []
            
            for row in rows:
                forme = row.forme
                if forme in drawers:
                    drawers[forme].append({
                        "denomination": row.denomination,
                        "frequency": row.frequency
                    })
            
            # Calculer position géométrique
            row_pos = ((chip_number - 1) // 6) + 1
            col_pos = ((chip_number - 1) % 6) + 1
            
            return {
                "chip_number": chip_number,
                "position": f"R{row_pos}C{col_pos}",
                "row": row_pos,
                "column": col_pos,
                "universe": universe,
                "drawers": drawers,
                "geometric_info": KatulaTableIntegratedService._get_geometric_info(row_pos, col_pos),
                "total_entries": sum(len(drawer) for drawer in drawers.values())
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des données du chip: {str(e)}"}
    
    @staticmethod
    def analyze_table_patterns(
        db: Session, 
        universe: str
    ) -> Dict[str, Any]:
        """Analyse les patterns de la table de Katula"""
        
        try:
            # Récupérer la table complète
            table = KatulaTableIntegratedService.get_complete_katula_table(db, universe)
            
            if "error" in table:
                return table
            
            # Analyser les patterns
            zone_stats = {}
            quadrant_stats = {}
            drawer_stats = {}
            
            for chip_info in table["chip_positions"].values():
                geo_info = chip_info["geometric_info"]
                
                # Stats par zone
                zone = geo_info["geometric_zone"]
                if zone not in zone_stats:
                    zone_stats[zone] = {"chips": 0, "total_entries": 0}
                zone_stats[zone]["chips"] += 1
                
                # Stats par quadrant
                quadrant = geo_info["quadrant"]
                if quadrant not in quadrant_stats:
                    quadrant_stats[quadrant] = {"chips": 0, "total_entries": 0}
                quadrant_stats[quadrant]["chips"] += 1
                
                # Stats par tiroir
                for drawer_name, drawer_data in chip_info["drawers"].items():
                    if drawer_name not in drawer_stats:
                        drawer_stats[drawer_name] = {"total_denominations": 0, "total_frequency": 0}
                    
                    drawer_stats[drawer_name]["total_denominations"] += len(drawer_data)
                    drawer_stats[drawer_name]["total_frequency"] += sum(item["frequency"] for item in drawer_data)
                    
                    zone_stats[zone]["total_entries"] += len(drawer_data)
                    quadrant_stats[quadrant]["total_entries"] += len(drawer_data)
            
            return {
                "universe": universe,
                "analysis_type": "table_patterns",
                "zone_analysis": zone_stats,
                "quadrant_analysis": quadrant_stats,
                "drawer_analysis": drawer_stats,
                "total_chips": table["dimensions"]["total_chips"],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de l'analyse des patterns: {str(e)}"}