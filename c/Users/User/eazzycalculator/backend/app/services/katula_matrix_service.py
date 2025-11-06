"""
Service de Matrice Katula - Extraction et formatage des données
Extrait les informations de la table 'combinations' et les retourne sous forme de matrice
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

class KatulaMatrixService:
    """
    Service pour extraire les données de la table combinations et les formatter en matrice
    """
    
    @staticmethod
    def extract_combinations_matrix(
        db: Session, 
        universe: str = "mundo", 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Extrait les données de la table combinations et les retourne sous forme de matrice
        """
        try:
            # Requête pour extraire toutes les informations pertinentes
            query = """
                SELECT 
                    combination_id,
                    num1, num2,
                    chip, chip_id,
                    univers,
                    granque_name,
                    tome,
                    forme,
                    denomination,
                    created_at
                FROM combinations 
                WHERE univers = :universe 
                ORDER BY combination_id DESC
                LIMIT :limit
            """
            
            result = db.execute(text(query), {
                "universe": universe,
                "limit": limit
            })
            
            combinations = result.fetchall()
            
            if not combinations:
                return {
                    "error": "Aucune combinaison trouvée",
                    "universe": universe,
                    "total_found": 0
                }
            
            # Formatter les données en matrice
            matrix_data = []
            denominations_map = {}
            formes_map = {}
            
            for combo in combinations:
                # Données de base
                combo_data = {
                    "combination_id": combo.combination_id,
                    "numbers": f"{combo.num1}-{combo.num2}",
                    "num1": combo.num1,
                    "num2": combo.num2,
                    "chip": combo.chip,
                    "chip_id": combo.chip_id,
                    "universe": combo.univers,
                    "granque_name": getattr(combo, 'granque_name', None),
                    "tome": getattr(combo, 'tome', None),
                    "forme": getattr(combo, 'forme', None),
                    "denomination": getattr(combo, 'denomination', None),
                    "created_at": getattr(combo, 'created_at', None)
                }
                
                matrix_data.append(combo_data)
                
                # Construire les maps pour les dénominations et formes
                if combo_data["denomination"]:
                    if combo_data["denomination"] not in denominations_map:
                        denominations_map[combo_data["denomination"]] = []
                    denominations_map[combo_data["denomination"]].append(combo_data)
                
                if combo_data["forme"]:
                    if combo_data["forme"] not in formes_map:
                        formes_map[combo_data["forme"]] = []
                    formes_map[combo_data["forme"]].append(combo_data)
            
            # Statistiques et attributs
            stats = KatulaMatrixService._calculate_matrix_stats(matrix_data)
            
            return {
                "universe": universe,
                "total_combinations": len(matrix_data),
                "matrix_data": matrix_data,
                "denominations": denominations_map,
                "formes": formes_map,
                "statistics": stats,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de l'extraction: {str(e)}"}
    
    @staticmethod
    def get_katula_table_data(
        db: Session, 
        universe: str = "mundo"
    ) -> Dict[str, Any]:
        """
        Extrait spécifiquement les données pour la table_de_katula
        """
        try:
            # Vérifier d'abord si la table table_de_katula existe
            check_table_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'table_de_katula'
                );
            """
            
            table_exists = db.execute(text(check_table_query)).scalar()
            
            if table_exists:
                # Extraire de table_de_katula
                query = """
                    SELECT 
                        chip, ligne, colonne, forme, denomination, univers,
                        created_at, updated_at
                    FROM table_de_katula 
                    WHERE univers = :universe 
                    ORDER BY chip
                """
                
                result = db.execute(text(query), {"universe": universe})
                katula_data = result.fetchall()
                
                # Formatter en matrice
                matrix = []
                for row in katula_data:
                    matrix.append({
                        "chip": row.chip,
                        "ligne": row.ligne,
                        "colonne": row.colonne,
                        "forme": row.forme,
                        "denomination": row.denomination,
                        "universe": row.univers,
                        "created_at": getattr(row, 'created_at', None),
                        "updated_at": getattr(row, 'updated_at', None)
                    })
                
                return {
                    "source": "table_de_katula",
                    "universe": universe,
                    "matrix": matrix,
                    "total_entries": len(matrix),
                    "extraction_timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback vers combinations
                return KatulaMatrixService.extract_combinations_matrix(db, universe)
                
        except Exception as e:
            return {"error": f"Erreur lors de l'extraction table_de_katula: {str(e)}"}
    
    @staticmethod
    def _calculate_matrix_stats(matrix_data: List[Dict]) -> Dict[str, Any]:
        """
        Calcule les statistiques de la matrice
        """
        if not matrix_data:
            return {}
        
        # Compter les occurrences
        chip_counts = {}
        forme_counts = {}
        denomination_counts = {}
        tome_counts = {}
        
        for item in matrix_data:
            # Chips
            chip = item.get("chip")
            if chip:
                chip_counts[chip] = chip_counts.get(chip, 0) + 1
            
            # Formes
            forme = item.get("forme")
            if forme:
                forme_counts[forme] = forme_counts.get(forme, 0) + 1
            
            # Dénominations
            denomination = item.get("denomination")
            if denomination:
                denomination_counts[denomination] = denomination_counts.get(denomination, 0) + 1
            
            # Tomes
            tome = item.get("tome")
            if tome:
                tome_counts[tome] = tome_counts.get(tome, 0) + 1
        
        return {
            "chip_distribution": chip_counts,
            "forme_distribution": forme_counts,
            "denomination_distribution": denomination_counts,
            "tome_distribution": tome_counts,
            "most_frequent_chip": max(chip_counts.items(), key=lambda x: x[1]) if chip_counts else None,
            "most_frequent_forme": max(forme_counts.items(), key=lambda x: x[1]) if forme_counts else None,
            "most_frequent_denomination": max(denomination_counts.items(), key=lambda x: x[1]) if denomination_counts else None
        }
    
    @staticmethod
    def format_for_katula_service(
        db: Session, 
        universe: str = "mundo",
        format_type: str = "matrix"
    ) -> Dict[str, Any]:
        """
        Formate les données spécifiquement pour le service katula-table
        """
        try:
            # Extraire les données
            data = KatulaMatrixService.get_katula_table_data(db, universe)
            
            if "error" in data:
                return data
            
            if format_type == "matrix":
                # Format matrice 8x6 pour katula-table
                matrix_8x6 = [[None for _ in range(6)] for _ in range(8)]
                
                if "matrix" in data:
                    for item in data["matrix"]:
                        ligne = item.get("ligne", 1)
                        colonne = item.get("colonne", 1)
                        
                        # S'assurer que les indices sont dans les limites
                        if 1 <= ligne <= 8 and 1 <= colonne <= 6:
                            matrix_8x6[ligne-1][colonne-1] = {
                                "chip": item.get("chip"),
                                "forme": item.get("forme"),
                                "denomination": item.get("denomination"),
                                "position": f"L{ligne}C{colonne}"
                            }
                
                return {
                    "universe": universe,
                    "format": "matrix_8x6",
                    "matrix": matrix_8x6,
                    "dimensions": {"rows": 8, "columns": 6},
                    "source": data.get("source", "combinations"),
                    "timestamp": datetime.now().isoformat()
                }
            
            elif format_type == "list":
                # Format liste pour katula-table
                return {
                    "universe": universe,
                    "format": "list",
                    "data": data.get("matrix", data.get("matrix_data", [])),
                    "source": data.get("source", "combinations"),
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                return data
                
        except Exception as e:
            return {"error": f"Erreur lors du formatage: {str(e)}"}