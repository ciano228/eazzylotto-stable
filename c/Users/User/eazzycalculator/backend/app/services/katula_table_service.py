"""
Service de Table de Katula
Système de matrice géométrique 8x6 pour la visualisation spatiale des combinaisons
"""
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json
from .katula_matrix_service import KatulaMatrixService

class KatulaTableService:
    """
    Service pour la gestion de la Table de Katula - Matrice géométrique 8x6
    """
    
    # Configuration de la matrice 8 lignes x 6 colonnes = 48 chips
    MATRIX_ROWS = 8
    MATRIX_COLS = 6
    TOTAL_CHIPS = 48
    
    @staticmethod
    def create_katula_table(universe: str = "mundo") -> Dict[str, Any]:
        """Crée la structure de base de la Table de Katula"""
        
        table = {
            "universe": universe,
            "name": f"table_de_katula_{universe}",
            "dimensions": {
                "rows": KatulaTableService.MATRIX_ROWS,
                "columns": KatulaTableService.MATRIX_COLS,
                "total_chips": KatulaTableService.TOTAL_CHIPS
            },
            "matrix": [],
            "chip_positions": {},
            "geometric_attributes": {}
        }
        
        # Créer la matrice 8x6
        chip_counter = 1
        for row in range(1, KatulaTableService.MATRIX_ROWS + 1):
            matrix_row = []
            for col in range(1, KatulaTableService.MATRIX_COLS + 1):
                chip_id = f"chip{chip_counter}"
                
                cell = {
                    "chip_id": chip_id,
                    "chip_number": chip_counter,
                    "row": row,
                    "column": col,
                    "position": f"R{row}C{col}",
                    "geometric_zone": KatulaTableService._get_geometric_zone(row, col),
                    "quadrant": KatulaTableService._get_quadrant(row, col),
                    "diagonal": KatulaTableService._get_diagonal_info(row, col),
                    "edge_info": KatulaTableService._get_edge_info(row, col)
                }
                
                matrix_row.append(cell)
                table["chip_positions"][chip_id] = cell
                chip_counter += 1
            
            table["matrix"].append(matrix_row)
        
        # Ajouter les attributs géométriques
        table["geometric_attributes"] = KatulaTableService._calculate_geometric_attributes()
        
        return table
    
    @staticmethod
    def _get_geometric_zone(row: int, col: int) -> str:
        """Détermine la zone géométrique d'une position"""
        
        # Diviser la matrice en zones
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
        
        return f"{vertical_zone}_{horizontal_zone}"
    
    @staticmethod
    def _get_quadrant(row: int, col: int) -> str:
        """Détermine le quadrant (4 zones principales)"""
        
        if row <= 4 and col <= 3:
            return "Q1_top_left"
        elif row <= 4 and col > 3:
            return "Q2_top_right"
        elif row > 4 and col <= 3:
            return "Q3_bottom_left"
        else:
            return "Q4_bottom_right"
    
    @staticmethod
    def _get_diagonal_info(row: int, col: int) -> Dict[str, Any]:
        """Calcule les informations diagonales"""
        
        # Diagonale principale (top-left à bottom-right)
        main_diagonal = (row - col) == -2  # Ajusté pour matrice 8x6
        
        # Diagonale secondaire (top-right à bottom-left)
        anti_diagonal = (row + col) == 7  # Ajusté pour matrice 8x6
        
        return {
            "on_main_diagonal": main_diagonal,
            "on_anti_diagonal": anti_diagonal,
            "diagonal_sum": row + col,
            "diagonal_diff": row - col
        }
    
    @staticmethod
    def _get_edge_info(row: int, col: int) -> Dict[str, Any]:
        """Détermine si la position est sur un bord"""
        
        is_top_edge = row == 1
        is_bottom_edge = row == KatulaTableService.MATRIX_ROWS
        is_left_edge = col == 1
        is_right_edge = col == KatulaTableService.MATRIX_COLS
        
        is_corner = (is_top_edge or is_bottom_edge) and (is_left_edge or is_right_edge)
        is_edge = is_top_edge or is_bottom_edge or is_left_edge or is_right_edge
        
        return {
            "is_corner": is_corner,
            "is_edge": is_edge,
            "is_center": not is_edge,
            "edge_type": KatulaTableService._get_edge_type(row, col)
        }
    
    @staticmethod
    def _get_edge_type(row: int, col: int) -> str:
        """Détermine le type de bord"""
        
        if row == 1 and col == 1:
            return "top_left_corner"
        elif row == 1 and col == KatulaTableService.MATRIX_COLS:
            return "top_right_corner"
        elif row == KatulaTableService.MATRIX_ROWS and col == 1:
            return "bottom_left_corner"
        elif row == KatulaTableService.MATRIX_ROWS and col == KatulaTableService.MATRIX_COLS:
            return "bottom_right_corner"
        elif row == 1:
            return "top_edge"
        elif row == KatulaTableService.MATRIX_ROWS:
            return "bottom_edge"
        elif col == 1:
            return "left_edge"
        elif col == KatulaTableService.MATRIX_COLS:
            return "right_edge"
        else:
            return "center"
    
    @staticmethod
    def _calculate_geometric_attributes() -> Dict[str, Any]:
        """Calcule les attributs géométriques globaux"""
        
        return {
            "zones": [
                "top_left", "top_center", "top_right",
                "middle_left", "middle_center", "middle_right",
                "bottom_left", "bottom_center", "bottom_right"
            ],
            "quadrants": ["Q1_top_left", "Q2_top_right", "Q3_bottom_left", "Q4_bottom_right"],
            "edge_types": [
                "top_left_corner", "top_right_corner", "bottom_left_corner", "bottom_right_corner",
                "top_edge", "bottom_edge", "left_edge", "right_edge", "center"
            ],
            "total_positions": KatulaTableService.TOTAL_CHIPS
        }
    
    @staticmethod
    def map_combination_to_katula(
        db: Session, 
        combination_id: int, 
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """Mappe une combinaison sur la Table de Katula en utilisant les données les plus récentes"""
        
        try:
            # Utiliser le nouveau service pour récupérer les données
            matrix_data = KatulaMatrixService.extract_combinations_matrix(db, universe, 1000)
            
            if "error" in matrix_data:
                return matrix_data
            
            # Trouver la combinaison spécifique
            target_combination = None
            for combo in matrix_data["matrix_data"]:
                if combo["combination_id"] == combination_id:
                    target_combination = combo
                    break
            
            if not target_combination:
                return {"error": "Combinaison non trouvée"}
            
            # Créer la table de Katula
            katula_table = KatulaTableService.create_katula_table(universe)
            
            # Mapper le chip sur la matrice
            chip_number = target_combination["chip_id"] if target_combination["chip_id"] else 1
            
            # S'assurer que le chip est dans la plage 1-48
            if chip_number < 1 or chip_number > 48:
                chip_number = ((chip_number - 1) % 48) + 1
            
            chip_id = f"chip{chip_number}"
            
            if chip_id in katula_table["chip_positions"]:
                position_info = katula_table["chip_positions"][chip_id]
                
                return {
                    "combination_id": target_combination["combination_id"],
                    "numbers": target_combination["numbers"],
                    "chip_mapping": {
                        "chip_id": chip_id,
                        "chip_number": chip_number,
                        "position": position_info["position"],
                        "row": position_info["row"],
                        "column": position_info["column"],
                        "geometric_zone": position_info["geometric_zone"],
                        "quadrant": position_info["quadrant"],
                        "diagonal_info": position_info["diagonal"],
                        "edge_info": position_info["edge_info"]
                    },
                    "denomination": target_combination.get("denomination"),
                    "forme": target_combination.get("forme"),
                    "granque_name": target_combination.get("granque_name"),
                    "tome": target_combination.get("tome"),
                    "universe": universe,
                    "mapping_timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"Chip {chip_id} non trouvé dans la table"}
                
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def analyze_historical_patterns(
        db: Session, 
        universe: str = "mundo", 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Analyse les patterns historiques sur la Table de Katula"""
        
        try:
            # Récupérer les combinaisons récentes avec nouvelles colonnes
            query = """
                SELECT c.combination_id, c.num1, c.num2, c.chip, c.chip_id, 
                       c.granque_name, c.tome, t.ligne, t.colonne, t.forme
                FROM combinations c
                LEFT JOIN table_de_katula t ON c.univers = t.univers AND c.chip = t.chip
                WHERE c.univers = :universe 
                ORDER BY c.combination_id DESC
                LIMIT :limit
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "limit": limit
            })
            
            combinations = result.fetchall()
            
            # Créer la table de Katula
            katula_table = KatulaTableService.create_katula_table(universe)
            
            # Analyser les patterns
            zone_frequency = {}
            quadrant_frequency = {}
            edge_frequency = {}
            position_history = []
            
            for combo in combinations:
                chip_number = combo.chip_id if combo.chip_id else 1
                if chip_number < 1 or chip_number > 48:
                    chip_number = ((chip_number - 1) % 48) + 1
                
                chip_id = f"chip{chip_number}"
                
                if chip_id in katula_table["chip_positions"]:
                    pos_info = katula_table["chip_positions"][chip_id]
                    
                    # Compter les fréquences par zone
                    zone = pos_info["geometric_zone"]
                    zone_frequency[zone] = zone_frequency.get(zone, 0) + 1
                    
                    # Compter les fréquences par quadrant
                    quadrant = pos_info["quadrant"]
                    quadrant_frequency[quadrant] = quadrant_frequency.get(quadrant, 0) + 1
                    
                    # Compter les fréquences par type de bord
                    edge_type = pos_info["edge_info"]["edge_type"]
                    edge_frequency[edge_type] = edge_frequency.get(edge_type, 0) + 1
                    
                    # Historique des positions avec nouvelles colonnes
                    position_history.append({
                        "combination_id": combo.combination_id,
                        "numbers": f"{combo.num1}-{combo.num2}",
                        "position": pos_info["position"],
                        "zone": zone,
                        "quadrant": quadrant,
                        "row": pos_info["row"],
                        "column": pos_info["column"],
                        "granque_name": getattr(combo, 'granque_name', 'N/A'),
                        "tome": getattr(combo, 'tome', 'N/A'),
                        "ligne": getattr(combo, 'ligne', 'N/A'),
                        "colonne": getattr(combo, 'colonne', 'N/A'),
                        "forme": getattr(combo, 'forme', 'N/A')
                    })
            
            # Identifier les zones chaudes et froides
            total_combinations = len(combinations)
            hot_zones = []
            cold_zones = []
            
            for zone, freq in zone_frequency.items():
                frequency_ratio = freq / total_combinations
                if frequency_ratio > 0.15:  # Plus de 15%
                    hot_zones.append({"zone": zone, "frequency": freq, "ratio": frequency_ratio})
                elif frequency_ratio < 0.05:  # Moins de 5%
                    cold_zones.append({"zone": zone, "frequency": freq, "ratio": frequency_ratio})
            
            return {
                "universe": universe,
                "analysis_period": f"Last {len(combinations)} combinations",
                "katula_table": katula_table,
                "frequency_analysis": {
                    "by_zone": zone_frequency,
                    "by_quadrant": quadrant_frequency,
                    "by_edge_type": edge_frequency
                },
                "pattern_insights": {
                    "hot_zones": sorted(hot_zones, key=lambda x: x["ratio"], reverse=True),
                    "cold_zones": sorted(cold_zones, key=lambda x: x["ratio"]),
                    "most_active_quadrant": max(quadrant_frequency.items(), key=lambda x: x[1]) if quadrant_frequency else None
                },
                "position_history": position_history[:20],  # 20 plus récentes
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def predict_next_zones(
        db: Session, 
        universe: str = "mundo", 
        prediction_method: str = "frequency"
    ) -> Dict[str, Any]:
        """Prédit les prochaines zones probables basées sur les patterns"""
        
        try:
            # Analyser les patterns historiques
            analysis = KatulaTableService.analyze_historical_patterns(db, universe, 50)
            
            if "error" in analysis:
                return analysis
            
            predictions = []
            
            if prediction_method == "frequency":
                # Prédiction basée sur les fréquences
                zone_freq = analysis["frequency_analysis"]["by_zone"]
                total_freq = sum(zone_freq.values())
                
                for zone, freq in zone_freq.items():
                    probability = freq / total_freq if total_freq > 0 else 0
                    predictions.append({
                        "zone": zone,
                        "probability": probability,
                        "frequency": freq,
                        "prediction_method": "frequency_based"
                    })
                
                # Trier par probabilité décroissante
                predictions.sort(key=lambda x: x["probability"], reverse=True)
            
            elif prediction_method == "cold_zones":
                # Prédiction basée sur les zones froides (due pour sortir)
                cold_zones = analysis["pattern_insights"]["cold_zones"]
                
                for cold_zone in cold_zones:
                    predictions.append({
                        "zone": cold_zone["zone"],
                        "probability": 1 - cold_zone["ratio"],  # Inverse de la fréquence
                        "reason": "Zone froide - due pour sortir",
                        "prediction_method": "cold_zone_reversion"
                    })
            
            return {
                "universe": universe,
                "prediction_method": prediction_method,
                "predictions": predictions[:10],  # Top 10
                "recommended_zones": predictions[:3],  # Top 3 recommandations
                "prediction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_chip_neighbors(chip_number: int) -> Dict[str, Any]:
        """Retourne les chips voisins d'un chip donné"""
        if chip_number < 1 or chip_number > 48:
            return {"error": "Chip invalide"}
        
        row = ((chip_number - 1) // 6) + 1
        col = ((chip_number - 1) % 6) + 1
        
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 1 <= nr <= 8 and 1 <= nc <= 6:
                    neighbor_chip = (nr - 1) * 6 + nc
                    neighbors.append(neighbor_chip)
        
        return {"chip": chip_number, "neighbors": neighbors}
    
    @staticmethod
    def find_optimal_positions(universe: str = "mundo") -> List[int]:
        """Trouve les positions optimales basées sur la géométrie"""
        optimal_chips = []
        
        # Centres des quadrants
        optimal_chips.extend([8, 11, 32, 35])  # Positions centrales
        
        # Coins stratégiques
        optimal_chips.extend([1, 6, 43, 48])  # Coins de la matrice
        
        return sorted(set(optimal_chips))
    
    @staticmethod
    def calculate_distance_matrix() -> Dict[str, Dict[str, float]]:
        """Calcule la matrice des distances entre tous les chips"""
        distances = {}
        
        for chip1 in range(1, 49):
            row1 = ((chip1 - 1) // 6) + 1
            col1 = ((chip1 - 1) % 6) + 1
            distances[f"chip{chip1}"] = {}
            
            for chip2 in range(1, 49):
                row2 = ((chip2 - 1) // 6) + 1
                col2 = ((chip2 - 1) % 6) + 1
                
                # Distance euclidienne
                distance = ((row2 - row1) ** 2 + (col2 - col1) ** 2) ** 0.5
                distances[f"chip{chip1}"][f"chip{chip2}"] = round(distance, 2)
        
        return distances