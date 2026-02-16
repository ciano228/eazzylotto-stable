"""
Service d'Analyse par Caractère (Tome, Forme, Chip, etc.)
Analyse la fréquence d'apparition selon le type de marquage choisi
"""

from typing import Dict, List, Any
from collections import Counter
import psycopg2

class CharacterAnalysisService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def analyze_by_character(self, universe: str, session_data: Dict, 
                           marking_type: str) -> Dict[str, Any]:
        """Analyse selon le caractère choisi (tome, forme, chip, etc.)"""
        
        draws = session_data.get('draws', [])
        if not draws:
            return {"error": "Aucun tirage à analyser"}
        
        # Analyser selon le type de marquage
        if marking_type == 'tome':
            return self._analyze_tomes(universe, draws)
        elif marking_type == 'forme':
            return self._analyze_formes(universe, draws)
        elif marking_type == 'chip':
            return self._analyze_chips(universe, draws)
        elif marking_type == 'granque':
            return self._analyze_granques(universe, draws)
        elif marking_type == 'denomination':
            return self._analyze_denominations(universe, draws)
        else:
            return {"error": f"Type de marquage non supporté: {marking_type}"}
    
    def _analyze_tomes(self, universe: str, draws: List[Dict]) -> Dict[str, Any]:
        """Analyse des tomes"""
        tome_frequency = Counter()
        tome_positions = {}
        tome_draws = {}
        
        for draw in draws:
            for num in draw['numbers']:
                # Calculer le tome basé sur le numéro
                tome = f"tome{((num - 1) // 12) + 1}"
                
                tome_frequency[tome] += 1
                
                if tome not in tome_positions:
                    tome_positions[tome] = []
                    tome_draws[tome] = []
                
                # Position géométrique simulée
                ligne = ((num - 1) // 6) + 1
                colonne = ((num - 1) % 6) + 1
                
                tome_positions[tome].append({
                    'ligne': ligne,
                    'colonne': colonne,
                    'coordinates': f"{ligne}{colonne}",
                    'number': num
                })
                
                tome_draws[tome].append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'loto_name': draw['loto_name'],
                    'number': num
                })
        
        # Calculer les statistiques
        total_occurrences = sum(tome_frequency.values())
        tome_stats = {}
        
        for tome, count in tome_frequency.items():
            frequency_percent = (count / total_occurrences) * 100
            
            # Positions géométriques uniques
            unique_positions = list(set(
                pos['coordinates'] for pos in tome_positions[tome]
            ))
            
            tome_stats[tome] = {
                'count': count,
                'frequency_percent': frequency_percent,
                'unique_positions': len(unique_positions),
                'positions': tome_positions[tome],
                'draws': tome_draws[tome],
                'geometric_representation': self._get_tome_geometric_zones(tome_positions[tome])
            }
        
        return {
            'analysis_type': 'tome',
            'universe': universe,
            'total_draws': len(draws),
            'total_occurrences': total_occurrences,
            'tome_stats': tome_stats,
            'ranking': sorted(tome_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        }
    
    def _analyze_formes(self, universe: str, draws: List[Dict]) -> Dict[str, Any]:
        """Analyse des formes"""
        forme_frequency = Counter()
        forme_positions = {}
        forme_draws = {}
        
        formes_map = ['carre', 'triangle', 'cercle', 'rectangle']
        
        for draw in draws:
            for num in draw['numbers']:
                forme = formes_map[num % 4]
                
                forme_frequency[forme] += 1
                
                if forme not in forme_positions:
                    forme_positions[forme] = []
                    forme_draws[forme] = []
                
                ligne = ((num - 1) // 6) + 1
                colonne = ((num - 1) % 6) + 1
                
                forme_positions[forme].append({
                    'ligne': ligne,
                    'colonne': colonne,
                    'coordinates': f"{ligne}{colonne}",
                    'number': num
                })
                
                forme_draws[forme].append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'loto_name': draw['loto_name'],
                    'number': num
                })
        
        total_occurrences = sum(forme_frequency.values())
        forme_stats = {}
        
        for forme, count in forme_frequency.items():
            frequency_percent = (count / total_occurrences) * 100
            
            unique_positions = list(set(
                pos['coordinates'] for pos in forme_positions[forme]
            ))
            
            forme_stats[forme] = {
                'count': count,
                'frequency_percent': frequency_percent,
                'unique_positions': len(unique_positions),
                'positions': forme_positions[forme],
                'draws': forme_draws[forme],
                'geometric_representation': self._get_forme_geometric_zones(forme_positions[forme])
            }
        
        return {
            'analysis_type': 'forme',
            'universe': universe,
            'total_draws': len(draws),
            'total_occurrences': total_occurrences,
            'forme_stats': forme_stats,
            'ranking': sorted(forme_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        }
    
    def _analyze_chips(self, universe: str, draws: List[Dict]) -> Dict[str, Any]:
        """Analyse des chips"""
        chip_frequency = Counter()
        chip_draws = {}
        
        for draw in draws:
            for num in draw['numbers']:
                chip_id = ((num - 1) // 6) * 6 + ((num - 1) % 6) + 1
                
                chip_frequency[chip_id] += 1
                
                if chip_id not in chip_draws:
                    chip_draws[chip_id] = []
                
                chip_draws[chip_id].append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'loto_name': draw['loto_name'],
                    'number': num
                })
        
        total_occurrences = sum(chip_frequency.values())
        chip_stats = {}
        
        for chip_id, count in chip_frequency.items():
            frequency_percent = (count / total_occurrences) * 100
            
            ligne = ((chip_id - 1) // 6) + 1
            colonne = ((chip_id - 1) % 6) + 1
            
            chip_stats[chip_id] = {
                'count': count,
                'frequency_percent': frequency_percent,
                'position': {
                    'ligne': ligne,
                    'colonne': colonne,
                    'coordinates': f"{ligne}{colonne}"
                },
                'draws': chip_draws[chip_id],
                'quadrant': self._get_quadrant(ligne, colonne)
            }
        
        return {
            'analysis_type': 'chip',
            'universe': universe,
            'total_draws': len(draws),
            'total_occurrences': total_occurrences,
            'chip_stats': chip_stats,
            'ranking': sorted(chip_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        }
    
    def _analyze_granques(self, universe: str, draws: List[Dict]) -> Dict[str, Any]:
        """Analyse des granques"""
        granque_frequency = Counter()
        granque_positions = {}
        granque_draws = {}
        
        for draw in draws:
            for num in draw['numbers']:
                granque = f"Q{((num - 1) // 8) + 1}"
                
                granque_frequency[granque] += 1
                
                if granque not in granque_positions:
                    granque_positions[granque] = []
                    granque_draws[granque] = []
                
                ligne = ((num - 1) // 6) + 1
                colonne = ((num - 1) % 6) + 1
                
                granque_positions[granque].append({
                    'ligne': ligne,
                    'colonne': colonne,
                    'coordinates': f"{ligne}{colonne}",
                    'number': num
                })
                
                granque_draws[granque].append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'loto_name': draw['loto_name'],
                    'number': num
                })
        
        total_occurrences = sum(granque_frequency.values())
        granque_stats = {}
        
        for granque, count in granque_frequency.items():
            frequency_percent = (count / total_occurrences) * 100
            
            unique_positions = list(set(
                pos['coordinates'] for pos in granque_positions[granque]
            ))
            
            granque_stats[granque] = {
                'count': count,
                'frequency_percent': frequency_percent,
                'unique_positions': len(unique_positions),
                'positions': granque_positions[granque],
                'draws': granque_draws[granque],
                'geometric_representation': self._get_granque_geometric_zones(granque_positions[granque])
            }
        
        return {
            'analysis_type': 'granque',
            'universe': universe,
            'total_draws': len(draws),
            'total_occurrences': total_occurrences,
            'granque_stats': granque_stats,
            'ranking': sorted(granque_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        }
    
    def _analyze_denominations(self, universe: str, draws: List[Dict]) -> Dict[str, Any]:
        """Analyse des dénominations"""
        denom_frequency = Counter()
        denom_draws = {}
        
        for draw in draws:
            for num in draw['numbers']:
                # Générer une dénomination simulée
                denom = f"denom_{num}_{draw['period']}"
                
                denom_frequency[denom] += 1
                
                if denom not in denom_draws:
                    denom_draws[denom] = []
                
                denom_draws[denom].append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'loto_name': draw['loto_name'],
                    'number': num
                })
        
        total_occurrences = sum(denom_frequency.values())
        denom_stats = {}
        
        for denom, count in denom_frequency.items():
            frequency_percent = (count / total_occurrences) * 100
            
            denom_stats[denom] = {
                'count': count,
                'frequency_percent': frequency_percent,
                'draws': denom_draws[denom]
            }
        
        return {
            'analysis_type': 'denomination',
            'universe': universe,
            'total_draws': len(draws),
            'total_occurrences': total_occurrences,
            'denomination_stats': denom_stats,
            'ranking': sorted(denom_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        }
    
    def _get_tome_geometric_zones(self, positions: List[Dict]) -> Dict[str, Any]:
        """Représentation géométrique d'un tome"""
        quadrants = Counter()
        zones = Counter()
        
        for pos in positions:
            ligne, colonne = pos['ligne'], pos['colonne']
            
            # Quadrant
            if ligne <= 4 and colonne <= 3:
                quadrants['Q1'] += 1
            elif ligne <= 4 and colonne > 3:
                quadrants['Q2'] += 1
            elif ligne > 4 and colonne <= 3:
                quadrants['Q3'] += 1
            else:
                quadrants['Q4'] += 1
            
            # Zone
            if ligne <= 3:
                v_zone = "top"
            elif ligne <= 6:
                v_zone = "middle"
            else:
                v_zone = "bottom"
            
            if colonne <= 2:
                h_zone = "left"
            elif colonne <= 4:
                h_zone = "center"
            else:
                h_zone = "right"
            
            zones[f"{v_zone}_{h_zone}"] += 1
        
        return {
            'quadrant_distribution': dict(quadrants),
            'zone_distribution': dict(zones),
            'total_positions': len(positions)
        }
    
    def _get_forme_geometric_zones(self, positions: List[Dict]) -> Dict[str, Any]:
        """Représentation géométrique d'une forme"""
        return self._get_tome_geometric_zones(positions)
    
    def _get_granque_geometric_zones(self, positions: List[Dict]) -> Dict[str, Any]:
        """Représentation géométrique d'une granque"""
        return self._get_tome_geometric_zones(positions)
    
    def _get_quadrant(self, ligne: int, colonne: int) -> str:
        """Détermine le quadrant"""
        if ligne <= 4 and colonne <= 3:
            return "Q1"
        elif ligne <= 4 and colonne > 3:
            return "Q2"
        elif ligne > 4 and colonne <= 3:
            return "Q3"
        else:
            return "Q4"