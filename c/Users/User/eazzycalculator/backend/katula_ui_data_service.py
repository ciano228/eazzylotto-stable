"""
Service de données UI pour Katula
"""
from typing import Dict, List, Any
import psycopg2
from katula_ui_mapper import KatulaUIMapper

class KatulaUIDataService:
    """Service pour préparer les données UI de Katula"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.mapper = KatulaUIMapper()
    
    def get_ui_data(self, universe: str) -> Dict[str, Any]:
        """Récupère les données formatées pour l'UI"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer toutes les données nécessaires
            cursor.execute("""
                SELECT 
                    chip_id,
                    univers,
                    ligne,
                    colonne,
                    petique,
                    forme,
                    denomination,
                    ARRAY_AGG(DISTINCT combinaison) as combinations
                FROM table_de_katula t
                LEFT JOIN table_combinations c ON 
                    t.chip_id = c.chip_id AND 
                    t.forme = c.forme AND 
                    t.denomination = c.denomination
                WHERE univers = %s
                GROUP BY 
                    t.chip_id,
                    t.univers,
                    t.ligne,
                    t.colonne,
                    t.petique,
                    t.forme,
                    t.denomination
                ORDER BY chip_id, forme
            """, (universe,))
            
            raw_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Organiser les données par quadrant et chip
            ui_data = self._organize_data(raw_data)
            
            return ui_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def _organize_data(self, raw_data: List[tuple]) -> Dict[str, Any]:
        """Organise les données pour l'UI"""
        # Structure de base
        organized = {
            "quadrants": {
                "Q1": {"chips": {}},
                "Q2": {"chips": {}},
                "Q3": {"chips": {}},
                "Q4": {"chips": {}}
            },
            "matrix": {
                str(i): {str(j): None for j in range(1, 7)} 
                for i in range(1, 9)
            }
        }
        
        # Organiser les données par position
        for row in raw_data:
            db_data = {
                "chip_id": row[0],
                "univers": row[1],
                "ligne": row[2],
                "colonne": row[3],
                "petique": row[4],
                "forme": row[5],
                "denomination": row[6],
                "combinations": row[7] if row[7] else []
            }
            
            # Convertir en élément UI
            ui_element = self.mapper.map_db_to_ui(db_data)
            
            # Ajouter à la matrice
            ligne = db_data["ligne"].replace("L", "")
            colonne = db_data["colonne"].replace("C", "")
            
            if organized["matrix"][ligne][colonne] is None:
                organized["matrix"][ligne][colonne] = {
                    "chip_id": db_data["chip_id"],
                    "elements": []
                }
            
            organized["matrix"][ligne][colonne]["elements"].append(ui_element)
            
            # Ajouter au quadrant approprié
            quadrant = ui_element.metadata["quadrant"]
            chip_id = str(db_data["chip_id"])
            
            if chip_id not in organized["quadrants"][quadrant]["chips"]:
                organized["quadrants"][quadrant]["chips"][chip_id] = []
            
            organized["quadrants"][quadrant]["chips"][chip_id].append(ui_element)
        
        return organized