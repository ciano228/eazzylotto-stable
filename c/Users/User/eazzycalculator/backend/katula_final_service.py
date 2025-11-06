"""
Service Katula Final - Géométrie variable avec quadrants délimités
"""
import psycopg2
from typing import Dict, List, Any

class KatulaFinalService:
    """Service final avec géométrie variable et quadrants délimités"""
    
    # Couleurs précises pour les formes
    FORME_COLORS = {
        'carre': '#2196F3',      # Bleu
        'triangle': '#4CAF50',   # Vert  
        'cercle': '#FFEB3B',     # Jaune
        'rectangle': '#F44336',  # Rouge
        # Composites (couleurs mélangées)
        'carre-triangle': 'linear-gradient(45deg, #2196F3, #4CAF50)',
        'carre-cercle': 'linear-gradient(45deg, #2196F3, #FFEB3B)',
        'carre-rectangle': 'linear-gradient(45deg, #2196F3, #F44336)',
        'triangle-carre': 'linear-gradient(45deg, #4CAF50, #2196F3)',
        'triangle-cercle': 'linear-gradient(45deg, #4CAF50, #FFEB3B)',
        'triangle-rectangle': 'linear-gradient(45deg, #4CAF50, #F44336)',
        'cercle-carre': 'linear-gradient(45deg, #FFEB3B, #2196F3)',
        'cercle-triangle': 'linear-gradient(45deg, #FFEB3B, #4CAF50)',
        'cercle-rectangle': 'linear-gradient(45deg, #FFEB3B, #F44336)',
        'rectangle-carre': 'linear-gradient(45deg, #F44336, #2196F3)',
        'rectangle-triangle': 'linear-gradient(45deg, #F44336, #4CAF50)',
        'rectangle-cercle': 'linear-gradient(45deg, #F44336, #FFEB3B)'
    }
    
    # Icônes pour les formes
    FORME_ICONS = {
        'carre': '■',
        'triangle': '▲', 
        'cercle': '●',
        'rectangle': '▬'
    }
    
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
    
    def get_universe_geometry(self, universe: str) -> Dict[str, Any]:
        """Détermine la géométrie variable par univers"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Compter les formes distinctes pour cet univers
            cursor.execute("""
                SELECT DISTINCT forme, COUNT(*) as count
                FROM table_de_katula 
                WHERE univers = %s AND forme IS NOT NULL
                GROUP BY forme
                ORDER BY forme
            """, (universe,))
            
            formes_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            formes = [f[0] for f in formes_data]
            
            # Déterminer le type de géométrie
            simples = [f for f in formes if '-' not in f]
            composites = [f for f in formes if '-' in f]
            
            return {
                "universe": universe,
                "total_formes": len(formes),
                "simples": simples,
                "composites": composites,
                "compartments_per_chip": len(formes) if len(formes) <= 16 else 16,
                "geometry_type": self._get_geometry_type(len(simples), len(composites))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_geometry_type(self, simples_count: int, composites_count: int) -> str:
        """Détermine le type de géométrie"""
        if simples_count == 4 and composites_count == 0:
            return "simple_4"  # Mundo, Fruity
        elif simples_count == 4 and composites_count == 12:
            return "variable_16"  # Trigga, Sunshine
        elif simples_count == 0 and composites_count == 12:
            return "composite_12"  # Roaster
        else:
            return "custom"
    
    def get_matrix_with_quadrants(self, universe: str) -> Dict[str, Any]:
        """Récupère la matrice avec quadrants délimités"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer toutes les données avec lignes/colonnes
            cursor.execute("""
                SELECT chip_id, ligne, colonne, forme, denomination, petique, tome, granque_name
                FROM table_de_katula 
                WHERE univers = %s
                ORDER BY chip_id, forme
            """, (universe,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Organiser par chip
            chips_data = {}
            for result in results:
                chip_id, ligne, colonne, forme, denomination, petique, tome, granque_name = result
                
                if chip_id not in chips_data:
                    chips_data[chip_id] = {
                        "chip_number": chip_id,
                        "ligne": ligne,
                        "colonne": colonne,
                        "petique": petique,
                        "tome": tome,
                        "granque_name": granque_name,
                        "compartments": [],
                        "quadrant": self._get_quadrant_from_position(ligne, colonne)
                    }
                
                if forme and denomination:
                    chips_data[chip_id]["compartments"].append({
                        "forme": forme,
                        "denomination": denomination,
                        "color": self.FORME_COLORS.get(forme, '#999'),
                        "icon": self._get_forme_icon(forme)
                    })
            
            # Créer la matrice 8x6
            matrix = {}
            for row in range(1, 9):
                matrix[row] = {}
                for col in range(1, 7):
                    chip_number = (row - 1) * 6 + col
                    matrix[row][col] = chips_data.get(chip_number, {
                        "chip_number": chip_number,
                        "ligne": f"L{row}",
                        "colonne": f"C{col}",
                        "compartments": [],
                        "quadrant": self._get_quadrant_from_position(f"L{row}", f"C{col}")
                    })
            
            geometry = self.get_universe_geometry(universe)
            
            return {
                "universe": universe,
                "matrix": matrix,
                "geometry": geometry,
                "quadrant_delimiters": {
                    "vertical_line": {"after_column": 3, "before_column": 4},
                    "horizontal_line": {"after_row": 4, "before_row": 5}
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_quadrant_from_position(self, ligne: str, colonne: str) -> str:
        """Détermine le quadrant depuis la position"""
        row = int(ligne.replace('L', ''))
        col = int(colonne.replace('C', ''))
        
        if row <= 4 and col <= 3:
            return "q1"
        elif row <= 4 and col > 3:
            return "q2"
        elif row > 4 and col <= 3:
            return "q3"
        else:
            return "q4"
    
    def _get_forme_icon(self, forme: str) -> str:
        """Retourne l'icône pour une forme"""
        if '-' in forme:
            # Forme composite - combiner les icônes
            parts = forme.split('-')
            icons = [self.FORME_ICONS.get(part, '?') for part in parts]
            return ''.join(icons)
        else:
            return self.FORME_ICONS.get(forme, '?')
    
    def get_filter_options(self, universe: str) -> Dict[str, Any]:
        """Options de filtrage avec lignes/colonnes"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ARRAY_AGG(DISTINCT forme) as formes,
                    ARRAY_AGG(DISTINCT petique) as petiques,
                    ARRAY_AGG(DISTINCT tome) as tomes,
                    ARRAY_AGG(DISTINCT granque_name) as granques,
                    ARRAY_AGG(DISTINCT ligne) as lignes,
                    ARRAY_AGG(DISTINCT colonne) as colonnes
                FROM table_de_katula 
                WHERE univers = %s
            """, (universe,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return {
                "universe": universe,
                "filter_options": {
                    "formes": sorted([f for f in result[0] if f]),
                    "petiques": sorted([p for p in result[1] if p]),
                    "tomes": sorted([t for t in result[2] if t]),
                    "granques": sorted([g for g in result[3] if g]),
                    "lignes": sorted([l for l in result[4] if l]),
                    "colonnes": sorted([c for c in result[5] if c]),
                    "quadrants": ["q1", "q2", "q3", "q4"]
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_denomination_details(self, universe: str, denomination: str) -> Dict[str, Any]:
        """Détails d'une dénomination cliquable"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT chip_id, ligne, colonne, forme, petique, tome, granque_name
                FROM table_de_katula 
                WHERE univers = %s AND denomination = %s
                ORDER BY chip_id
            """, (universe, denomination))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            details = []
            for result in results:
                details.append({
                    "chip_id": result[0],
                    "position": f"{result[1]}{result[2]}",
                    "forme": result[3],
                    "petique": result[4],
                    "tome": result[5],
                    "granque_name": result[6]
                })
            
            return {
                "universe": universe,
                "denomination": denomination,
                "occurrences": len(details),
                "details": details
            }
            
        except Exception as e:
            return {"error": str(e)}

# Instance globale
katula_final_service = KatulaFinalService()