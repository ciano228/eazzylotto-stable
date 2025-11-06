"""
Service Katula Complet avec ordre des formes et filtrage avancé
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import psycopg2
from enum import Enum

class UniverseType(Enum):
    BASIC = 'BASIC'       # Formes simples uniquement (mundo, fruity)
    COMPOUND = 'COMPOUND' # Formes composées uniquement (roaster)
    HYBRID = 'HYBRID'     # Mix de formes simples et composées (trigga, sunshine)

@dataclass
class UniverseConfig:
    name: str
    type: UniverseType
    forms: List[str]
    description: str
    rows: int = 8
    cols: int = 6
    
    @property
    def total_chips(self) -> int:
        return self.rows * self.cols

@dataclass
class ChipCompartment:
    """Compartiment d'un chip avec ordre précis"""
    position: int  # Position dans le chip (1 à N)
    forme: str
    denomination: str
    petique: str
    tome: str
    granque_name: str

class KatulaCompleteService:
    """Service complet pour la table Katula avec ordre et filtrage"""
    
    # Configuration des univers
    UNIVERSES: Dict[str, UniverseConfig] = {
        'mundo': UniverseConfig(
            name='mundo',
            type=UniverseType.BASIC,
            forms=['carre', 'triangle', 'cercle', 'rectangle'],
            description='4 formes de base',
            rows=8,
            cols=6
        ),
        'fruity': UniverseConfig(
            name='fruity',
            type=UniverseType.BASIC,
            forms=['carre', 'triangle', 'cercle', 'rectangle'],
            description='4 formes de base',
            rows=8,
            cols=6
        ),
        'trigga': UniverseConfig(
            name='trigga',
            type=UniverseType.HYBRID,
            forms=[
                'carre', 'triangle', 'cercle', 'rectangle',
                'carre-triangle', 'carre-cercle', 'carre-rectangle',
                'triangle-carre', 'triangle-cercle', 'triangle-rectangle',
                'cercle-rectangle'  # 10 formes au total
            ],
            description='4 formes de base + 6 combinaisons',
            rows=8,
            cols=6
        ),
        'roaster': UniverseConfig(
            name='roaster',
            type=UniverseType.COMPOUND,
            forms=[
                'carre-triangle', 'carre-cercle', 'carre-rectangle',
                'triangle-carre', 'triangle-cercle', 'triangle-rectangle',
                'cercle-carre', 'cercle-triangle', 'cercle-rectangle',
                'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle'
            ],
            description='12 formes composées',
            rows=8,
            cols=6
        ),
        'sunshine': UniverseConfig(
            name='sunshine',
            type=UniverseType.HYBRID,
            forms=[
                'carre', 'triangle', 'cercle', 'rectangle',
                'carre-triangle', 'carre-cercle', 'carre-rectangle',
                'triangle-carre', 'triangle-cercle', 'triangle-rectangle',
                'cercle-carre', 'cercle-triangle', 'cercle-rectangle',
                'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle'
            ],
            description='4 formes de base + 12 combinaisons',
            rows=8,
            cols=6
        )
    }
    
    def __init__(self):
        from config import DB_CONFIG
        self.db_config = DB_CONFIG
    
    def get_chip_compartments(self, universe: str, chip_number: int) -> Dict[str, Any]:
        """Récupère les compartiments d'un chip dans l'ordre exact avec dénominations et combinaisons"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer toutes les données du chip avec les combinaisons
            cursor.execute("""
                SELECT 
                    f.forme,
                    STRING_AGG(DISTINCT f.denomination, '/') as denominations,
                    f.petique,
                    f.tome,
                    f.granque_name,
                    STRING_AGG(DISTINCT c.combination_value || ' (pos:' || c.position || ')', ', ') as combinations
                FROM table_de_katula f
                LEFT JOIN table_combinations c ON 
                    f.chip_id = c.chip_id AND 
                    f.forme = c.forme AND 
                    f.denomination = c.denomination
                WHERE f.univers = %s AND f.chip_id = %s
                GROUP BY f.forme, f.petique, f.tome, f.granque_name
                ORDER BY f.forme
            """, (universe, chip_number))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Organiser selon l'ordre des formes
            compartments = []
            forme_order = self._get_forme_order_for_universe(universe)
            
            for position, forme in enumerate(forme_order, 1):
                # Trouver les données pour cette forme
                forme_data = [r for r in results if r[0] == forme]
                
                if forme_data:
                    for data in forme_data:
                        compartments.append(ChipCompartment(
                            position=position,
                            forme=data[0],
                            denomination=data[1],
                            petique=data[2],
                            tome=data[3],
                            granque_name=data[4]
                        ))
                else:
                    # Compartiment vide mais préservé dans l'ordre
                    compartments.append(ChipCompartment(
                        position=position,
                        forme=forme,
                        denomination="",
                        petique="",
                        tome="",
                        granque_name=""
                    ))
            
            return {
                "universe": universe,
                "chip_number": chip_number,
                "compartments": [c.__dict__ for c in compartments],
                "total_compartments": len(compartments)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_universe_config(self, universe: str) -> UniverseConfig:
        """Récupère la configuration d'un univers"""
        config = self.UNIVERSES.get(universe)
        if not config:
            raise ValueError(f"Univers inconnu: {universe}")
        return config
    
    def get_available_universes(self) -> List[Dict[str, Any]]:
        """Retourne la liste des univers disponibles avec leurs métadonnées"""
        return [
            {
                'name': config.name,
                'type': config.type.value,
                'total_forms': len(config.forms),
                'description': config.description,
                'rows': config.rows,
                'cols': config.cols,
                'total_chips': config.total_chips
            }
            for config in self.UNIVERSES.values()
        ]
    
    def _get_forme_order_for_universe(self, universe: str) -> List[str]:
        """Retourne l'ordre des formes pour un univers spécifique"""
        config = self.get_universe_config(universe)
        return config.forms.copy()
    
    def get_katula_table(self, universe: str) -> Dict[str, Any]:
        """Récupère les données de la table Katula pour un univers donné"""
        try:
            print(f"[DEBUG] Début de get_katula_table pour l'univers: {universe}")
            
            # 1. Vérifier la configuration de l'univers
            try:
                config = self.get_universe_config(universe)
                print(f"[DEBUG] Configuration de l'univers chargée: {config}")
            except Exception as e:
                error_msg = f"Erreur lors du chargement de la configuration de l'univers {universe}: {str(e)}"
                print(f"[ERROR] {error_msg}")
                return {
                    'error': error_msg,
                    'source': 'get_universe_config',
                    'status': 'error'
                }
            
            total_chips = config.rows * config.cols
            print(f"[DEBUG] Configuration: {config.rows} lignes x {config.cols} colonnes = {total_chips} chips")
            
            # 2. Se connecter à la base de données
            try:
                print(f"[DEBUG] Connexion à la base de données avec la configuration: {self.db_config}")
                conn = psycopg2.connect(**self.db_config)
                cursor = conn.cursor()
                print("[DEBUG] Connexion à la base de données établie")
                
                # 3. Exécuter la requête
                query = """
                    SELECT 
                        chip_id,
                        forme,
                        STRING_AGG(DISTINCT denomination, '/') as denominations,
                        petique,
                        tome,
                        granque_name
                    FROM table_de_katula
                    WHERE univers = %s
                    GROUP BY chip_id, forme, petique, tome, granque_name
                    ORDER BY chip_id, forme
                """
                print(f"[DEBUG] Exécution de la requête pour l'univers: {universe}")
                cursor.execute(query, (universe,))
                results = cursor.fetchall()
                print(f"[DEBUG] {len(results)} lignes récupérées")
                
            except Exception as e:
                error_msg = f"Erreur lors de l'exécution de la requête SQL: {str(e)}"
                print(f"[ERROR] {error_msg}")
                return {
                    'error': error_msg,
                    'source': 'database_query',
                    'status': 'error'
                }
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
                print("[DEBUG] Connexion à la base de données fermée")
            
            # 4. Traiter les résultats
            try:
                chips = {}
                for row in results:
                    chip_id = row[0]
                    if chip_id not in chips:
                        chips[chip_id] = []
                    chips[chip_id].append({
                        'forme': row[1],
                        'denomination': row[2],
                        'petique': row[3],
                        'tome': row[4],
                        'granque_name': row[5]
                    })
                
                # 5. Créer la matrice
                matrix = []
                for row in range(config.rows):
                    matrix_row = []
                    for col in range(config.cols):
                        chip_number = row * config.cols + col + 1
                        matrix_row.append({
                            'chip_number': chip_number,
                            'compartments': chips.get(chip_number, [])
                        })
                    matrix.append(matrix_row)
                
                response = {
                    'universe': universe,
                    'rows': config.rows,
                    'cols': config.cols,
                    'total_chips': total_chips,
                    'matrix': matrix,
                    'source': 'table_de_katula',
                    'status': 'success'
                }
                
                print(f"[DEBUG] Réponse générée avec succès pour l'univers {universe}")
                return response
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement des résultats: {str(e)}"
                print(f"[ERROR] {error_msg}")
                return {
                    'error': error_msg,
                    'source': 'data_processing',
                    'status': 'error'
                }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"Erreur inattendue dans get_katula_table: {str(e)}\n{error_trace}"
            print(f"[CRITICAL] {error_msg}")
            return {
                'error': error_msg,
                'source': 'unexpected',
                'status': 'error',
                'traceback': error_trace
            }
    
    def get_matrix_with_compartments(self, universe: str) -> Dict[str, Any]:
        """Récupère la matrice complète avec compartiments ordonnés"""
        config = self.get_universe_config(universe)
        matrix = {}
        chips_flat = {} # Flattened chips for easier frontend access
        
        # Get forme order for this universe
        forme_order = self._get_forme_order_for_universe(universe)

        # Prepare main_denomination for each chip
        # This requires iterating through compartments to find the first non-empty one
        # For now, let's just get the chip data and let frontend handle main_denomination
        # Or, we can add it here. Let's add it here for completeness.


        for chip_num in range(1, config.total_chips + 1):
            row = ((chip_num - 1) // config.cols) + 1
            col = ((chip_num - 1) % config.cols) + 1
            
            chip_data = self.get_chip_compartments(universe, chip_num)
            
            if row not in matrix:
                matrix[row] = {}

            compartments_dict = {c['forme']: c for c in chip_data.get("compartments", []) if c.get('denomination')}
            main_denomination = ""
            for forme in forme_order:
                if forme in compartments_dict:
                    main_denomination = compartments_dict[forme]['denomination']
                    break

            chip_entry = {
                "chip_number": chip_num,
                "position": f"L{row}C{col}",
                "compartments": compartments_dict, # Store as dict for easier access by forme
                "geometric_zone": self._get_geometric_zone(row, col, config.rows, config.cols),
                "quadrant": self._get_quadrant(row, col, config.rows, config.cols),
                "main_denomination": main_denomination
            }
            matrix[row][col] = chip_entry
            chips_flat[chip_num] = chip_entry

        return {
            "universe": universe,
            "matrix": matrix,
            "formes": forme_order, # Add formes here
            "chips": chips_flat, # Add flattened chips here
            "dimensions": {"rows": 8, "cols": 6, "total_chips": 48} # Keep dimensions
        }
    
    def apply_filters(self, universe: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Applique des filtres sur la matrice Katula"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Construire la requête avec filtres
            where_conditions = ["univers = %s"]
            params = [universe]
            
            # Filtres disponibles
            if filters.get('forme'):
                if isinstance(filters['forme'], list):
                    placeholders = ','.join(['%s'] * len(filters['forme']))
                    where_conditions.append(f"forme IN ({placeholders})")
                    params.extend(filters['forme'])
                else:
                    where_conditions.append("forme = %s")
                    params.append(filters['forme'])
            
            if filters.get('petique'):
                if isinstance(filters['petique'], list):
                    placeholders = ','.join(['%s'] * len(filters['petique']))
                    where_conditions.append(f"petique IN ({placeholders})")
                    params.extend(filters['petique'])
                else:
                    where_conditions.append("petique = %s")
                    params.append(filters['petique'])
            
            if filters.get('tome'):
                where_conditions.append("tome = %s")
                params.append(filters['tome'])
            
            if filters.get('granque_name'):
                where_conditions.append("granque_name = %s")
                params.append(filters['granque_name'])
            
            if filters.get('chip_range'):
                start, end = filters['chip_range']
                where_conditions.append("chip_id BETWEEN %s AND %s")
                params.extend([start, end])
            
            # Filtres géométriques
            if filters.get('quadrant'):
                # Convertir quadrant en plage de chips
                chip_ranges = self._quadrant_to_chip_range(filters['quadrant'])
                if chip_ranges:
                    range_conditions = []
                    for start, end in chip_ranges:
                        range_conditions.append("chip_id BETWEEN %s AND %s")
                        params.extend([start, end])
                    where_conditions.append(f"({' OR '.join(range_conditions)})")
            
            # Exécuter la requête
            query = f"""
                SELECT chip_id, forme, denomination, petique, tome, granque_name, ligne, colonne
                FROM table_de_katula 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY chip_id, forme
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Organiser les résultats par chip
            filtered_chips = {}
            for result in results:
                chip_id, forme, denomination, petique, tome, granque_name, ligne, colonne = result
                
                if chip_id not in filtered_chips:
                    filtered_chips[chip_id] = {
                        "chip_number": chip_id,
                        "position": f"{ligne}{colonne}",
                        "compartments": [],
                        "matches_filter": True
                    }
                
                filtered_chips[chip_id]["compartments"].append({
                    "forme": forme,
                    "denomination": denomination,
                    "petique": petique,
                    "tome": tome,
                    "granque_name": granque_name
                })
            
            return {
                "universe": universe,
                "filters_applied": filters,
                "filtered_chips": filtered_chips,
                "total_matches": len(filtered_chips)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_filter_options(self, universe: str) -> Dict[str, Any]:
        """Récupère toutes les options de filtrage disponibles"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer toutes les valeurs uniques pour chaque critère
            # Récupérer les valeurs distinctes
            cursor.execute("""
                SELECT 
                    ARRAY_AGG(DISTINCT forme) as formes,
                    ARRAY_AGG(DISTINCT petique) as petiques,
                    ARRAY_AGG(DISTINCT tome) as tomes,
                    ARRAY_AGG(DISTINCT granque_name) as granques
                FROM table_de_katula 
                WHERE univers = %s
            """, (universe,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            # S'assurer que les tomes sont bien ordonnés de tome1 à tome10
            tomes = [t for t in result[2] if t]
            tomes.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))  # Trie numériquement les tomes
            
            # Trier les résultats manuellement
            formes = sorted([f for f in result[0] if f])
            petiques = sorted([p for p in result[1] if p])
            tomes = sorted([t for t in result[2] if t], 
                         key=lambda x: int(''.join(filter(str.isdigit, x))))  # Tri numérique des tomes
            granques = sorted([g for g in result[3] if g])

            return {
                "universe": universe,
                "filter_options": {
                    "formes": formes,
                    "petiques": petiques,
                    "tomes": tomes,
                    "granques": granques,
                    "quadrants": ["Q1_top_left", "Q2_top_right", "Q3_bottom_left", "Q4_bottom_right"],
                    "geometric_zones": [
                        "top_left", "top_center", "top_right",
                        "middle_left", "middle_center", "middle_right",
                        "bottom_left", "bottom_center", "bottom_right"
                    ]
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_geometric_zone(self, row: int, col: int, total_rows: int, total_cols: int) -> str:
        """Détermine la zone géométrique"""
        # Déterminer la zone verticale
        if row <= total_rows // 3:
            v_zone = "top"
        elif row <= 2 * total_rows // 3:
            v_zone = "middle"
        else:
            v_zone = "bottom"
        
        # Déterminer la zone horizontale
        if col <= total_cols // 3:
            h_zone = "left"
        elif col <= 2 * total_cols // 3:
            h_zone = "center"
        else:
            h_zone = "right"
        
        return f"{v_zone}_{h_zone}"
    
    def _get_quadrant(self, row: int, col: int, total_rows: int, total_cols: int) -> str:
        """Détermine le quadrant"""
        row_mid = total_rows // 2
        col_mid = total_cols // 2
        
        if row <= row_mid and col <= col_mid:
            return "Q1_top_left"
        elif row <= row_mid and col > col_mid:
            return "Q2_top_right"
        elif row > row_mid and col <= col_mid:
            return "Q3_bottom_left"
        else:
            return "Q4_bottom_right"
    
    def _quadrant_to_chip_range(self, quadrant: str) -> List[tuple]:
        """Convertit un quadrant en plages de chips"""
        # Cette méthode est maintenant dépréciée car les plages dépendent de la configuration de l'univers
        # Elle est conservée pour la rétrocompatibilité
        ranges = {
            "Q1_top_left": [(1, 3), (7, 9), (13, 15), (19, 21)],
            "Q2_top_right": [(4, 6), (10, 12), (16, 18), (22, 24)],
            "Q3_bottom_left": [(25, 27), (31, 33), (37, 39), (43, 45)],
            "Q4_bottom_right": [(28, 30), (34, 36), (40, 42), (46, 48)]
        }
        return ranges.get(quadrant, [])
        
    def get_quadrant_ranges(self, universe: str) -> Dict[str, List[Tuple[int, int]]]:
        """Retourne les plages de chips pour chaque quadrant d'un univers spécifique"""
        config = self.get_universe_config(universe)
        rows = config.rows
        cols = config.cols
        
        # Calculer les limites des quadrants
        row_mid = rows // 2
        col_mid = cols // 2
        
        # Initialiser les plages
        q1 = []  # Q1_top_left
        q2 = []  # Q2_top_right
        q3 = []  # Q3_bottom_left
        q4 = []  # Q4_bottom_right
        
        # Parcourir tous les chips et les assigner aux quadrants
        for chip_num in range(1, config.total_chips + 1):
            row = ((chip_num - 1) // cols) + 1
            col = ((chip_num - 1) % cols) + 1
            
            if row <= row_mid and col <= col_mid:
                q1.append(chip_num)
            elif row <= row_mid and col > col_mid:
                q2.append(chip_num)
            elif row > row_mid and col <= col_mid:
                q3.append(chip_num)
            else:
                q4.append(chip_num)
        
        # Convertir les listes de numéros en plages consécutives
        def to_ranges(chip_numbers):
            if not chip_numbers:
                return []
                
            chip_numbers = sorted(chip_numbers)
            ranges = []
            start = chip_numbers[0]
            
            for i in range(1, len(chip_numbers)):
                if chip_numbers[i] != chip_numbers[i-1] + 1:
                    ranges.append((start, chip_numbers[i-1]))
                    start = chip_numbers[i]
            
            ranges.append((start, chip_numbers[-1]))
            return ranges
        
        return {
            "Q1_top_left": to_ranges(q1),
            "Q2_top_right": to_ranges(q2),
            "Q3_bottom_left": to_ranges(q3),
            "Q4_bottom_right": to_ranges(q4)
        }

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
            
            return {"details": details}
            
        except Exception as e:
            return {"error": str(e)}
# Instance globale
katula_service = KatulaCompleteService()