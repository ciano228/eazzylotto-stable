"""
Service de données UI pour Katula
"""
from typing import Dict, List, Any
import psycopg2
from .katula_ui_mapper import KatulaUIMapper

class KatulaUIDataService:
    """Service pour préparer les données UI de Katula"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.mapper = KatulaUIMapper()

    def get_formes(self) -> List[Dict[str, str]]:
        """Récupère la liste unique des formes avec leurs icônes"""
        # À terme, ce mappage pourrait être dans une table de configuration
        icon_map = {
            'cercle': '⭕',
            'triangle': '△',
            'carre': '□',
            'losange': '◇',
            'rectangle': '▭'
        }
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT forme FROM table_de_katula ORDER BY forme ASC")
            
            formes_from_db = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            # Associer les formes de la BD avec leurs icônes
            result = []
            for forme_name in formes_from_db:
                result.append({
                    'name': forme_name,
                    'icon': icon_map.get(forme_name.lower(), '?') # Utilise .get pour la sécurité
                })
            
            return result
            
        except Exception as e:
            # Log l'erreur ici si nécessaire
            return []
    
    def get_ui_data(self, universe: str) -> Dict[str, Any]:
        """Récupère les données et les transforme pour l'UI.""" 
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupération des données depuis la table combinations
            cursor.execute("""
                SELECT 
                    c.chip_id, 
                    c.univers, 
                    c.ligne, 
                    c.colonne, 
                    c.petique, 
                    c.forme, 
                    c.denomination,
                    c.combinations
                FROM combinations c
                WHERE c.univers = %s
                ORDER BY c.chip_id, c.forme
            """, (universe,))
            
            raw_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not raw_data:
                # Retourne une matrice vide si aucune donnée n'est trouvée
                return {"matrix": {str(i): {str(j): None for j in range(1, 7)} for i in range(1, 9)}}

            # Organise les données dans le format attendu par le frontend
            return self._organize_data(raw_data)
            
        except psycopg2.Error as e:
            print(f"ERREUR de base de données dans get_ui_data: {e}")
            return {"error": "Database error occurred", "details": str(e)}
        except Exception as e:
            print(f"ERREUR inattendue dans get_ui_data: {e}")
            return {"error": "An unexpected error occurred", "details": str(e)}
    
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