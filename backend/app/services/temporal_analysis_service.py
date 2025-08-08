"""
Service d'analyse temporelle pour la détection de patterns
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter

class TemporalAnalysisService:
    
    @staticmethod
    def get_temporal_data(
        db: Session, 
        universe: str, 
        date_start: str, 
        date_end: str, 
        marking_type: str = 'chip'
    ) -> Dict[str, Any]:
        """
        Récupère les données temporelles pour une période donnée
        
        Args:
            db: Session de base de données
            universe: Nom de l'univers (fruity, trigga, etc.)
            date_start: Date de début (YYYY-MM-DD)
            date_end: Date de fin (YYYY-MM-DD)
            marking_type: Type de marquage (chip, combination, denomination, etc.)
        
        Returns:
            Dict contenant les occurrences et métadonnées
        """
        try:
            # Requête adaptée selon le type de marquage
            if marking_type == 'chip':
                return TemporalAnalysisService._get_chip_data(db, universe, date_start, date_end)
            elif marking_type == 'combination':
                return TemporalAnalysisService._get_combination_data(db, universe, date_start, date_end)
            elif marking_type == 'denomination':
                return TemporalAnalysisService._get_denomination_data(db, universe, date_start, date_end)
            elif marking_type == 'tome':
                return TemporalAnalysisService._get_tome_data(db, universe, date_start, date_end)
            elif marking_type == 'forme':
                return TemporalAnalysisService._get_forme_data(db, universe, date_start, date_end)
            elif marking_type == 'granque':
                return TemporalAnalysisService._get_granque_data(db, universe, date_start, date_end)
            else:
                return TemporalAnalysisService._get_chip_data(db, universe, date_start, date_end)
                
        except Exception as e:
            print(f"Erreur dans get_temporal_data: {e}")
            return {
                'occurrences': {},
                'total_draws': 0,
                'period_info': {
                    'start': date_start,
                    'end': date_end,
                    'universe': universe,
                    'marking_type': marking_type
                }
            }
    
    @staticmethod
    def _get_chip_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par chip"""
        query = text(f"""
            SELECT 
                chip,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT denomination) as denominations,
                GROUP_CONCAT(DISTINCT forme) as formes,
                GROUP_CONCAT(DISTINCT tome) as tomes,
                GROUP_CONCAT(DISTINCT granque_name) as granques,
                MIN(date_tirage) as first_occurrence,
                MAX(date_tirage) as last_occurrence
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND chip IS NOT NULL
            GROUP BY chip
            ORDER BY chip
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                occurrences[chip_num] = {
                    'count': row.occurrence_count,
                    'attributes': (row.denominations or '').split(','),
                    'details': {
                        'denominations': (row.denominations or '').split(','),
                        'formes': (row.formes or '').split(','),
                        'tomes': (row.tomes or '').split(','),
                        'granques': (row.granques or '').split(','),
                        'first_occurrence': str(row.first_occurrence) if row.first_occurrence else None,
                        'last_occurrence': str(row.last_occurrence) if row.last_occurrence else None
                    }
                }
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'chip'
            }
        }
    
    @staticmethod
    def _get_combination_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par combinaison"""
        query = text(f"""
            SELECT 
                chip,
                combination_id,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT denomination) as denominations
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND combination_id IS NOT NULL
            GROUP BY chip, combination_id
            ORDER BY chip, combination_id
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                if chip_num not in occurrences:
                    occurrences[chip_num] = {'count': 0, 'attributes': [], 'details': []}
                
                occurrences[chip_num]['count'] += row.occurrence_count
                occurrences[chip_num]['attributes'].append(f"combo_{row.combination_id}")
                occurrences[chip_num]['details'].append({
                    'combination_id': row.combination_id,
                    'count': row.occurrence_count,
                    'denominations': (row.denominations or '').split(',')
                })
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'combination'
            }
        }
    
    @staticmethod
    def _get_denomination_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par dénomination"""
        query = text(f"""
            SELECT 
                chip,
                denomination,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT forme) as formes,
                GROUP_CONCAT(DISTINCT tome) as tomes
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND denomination IS NOT NULL
            GROUP BY chip, denomination
            ORDER BY chip, denomination
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                if chip_num not in occurrences:
                    occurrences[chip_num] = {'count': 0, 'attributes': [], 'details': []}
                
                occurrences[chip_num]['count'] += row.occurrence_count
                occurrences[chip_num]['attributes'].append(row.denomination)
                occurrences[chip_num]['details'].append({
                    'denomination': row.denomination,
                    'count': row.occurrence_count,
                    'formes': (row.formes or '').split(','),
                    'tomes': (row.tomes or '').split(',')
                })
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'denomination'
            }
        }
    
    @staticmethod
    def _get_tome_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par tome"""
        query = text(f"""
            SELECT 
                chip,
                tome,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT denomination) as denominations
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND tome IS NOT NULL
            GROUP BY chip, tome
            ORDER BY chip, tome
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                if chip_num not in occurrences:
                    occurrences[chip_num] = {'count': 0, 'attributes': [], 'details': []}
                
                occurrences[chip_num]['count'] += row.occurrence_count
                occurrences[chip_num]['attributes'].append(row.tome)
                occurrences[chip_num]['details'].append({
                    'tome': row.tome,
                    'count': row.occurrence_count,
                    'denominations': (row.denominations or '').split(',')
                })
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'tome'
            }
        }
    
    @staticmethod
    def _get_forme_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par forme"""
        query = text(f"""
            SELECT 
                chip,
                forme,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT denomination) as denominations
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND forme IS NOT NULL
            GROUP BY chip, forme
            ORDER BY chip, forme
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                if chip_num not in occurrences:
                    occurrences[chip_num] = {'count': 0, 'attributes': [], 'details': []}
                
                occurrences[chip_num]['count'] += row.occurrence_count
                occurrences[chip_num]['attributes'].append(row.forme)
                occurrences[chip_num]['details'].append({
                    'forme': row.forme,
                    'count': row.occurrence_count,
                    'denominations': (row.denominations or '').split(',')
                })
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'forme'
            }
        }
    
    @staticmethod
    def _get_granque_data(db: Session, universe: str, date_start: str, date_end: str) -> Dict[str, Any]:
        """Récupère les données par granque"""
        query = text(f"""
            SELECT 
                chip,
                granque_name,
                COUNT(*) as occurrence_count,
                GROUP_CONCAT(DISTINCT denomination) as denominations
            FROM {universe}
            WHERE date_tirage BETWEEN :date_start AND :date_end
            AND granque_name IS NOT NULL
            GROUP BY chip, granque_name
            ORDER BY chip, granque_name
        """)
        
        result = db.execute(query, {
            'date_start': date_start,
            'date_end': date_end
        })
        
        occurrences = {}
        total_draws = 0
        
        for row in result:
            chip_num = int(row.chip.replace('chip', '')) if row.chip and row.chip.startswith('chip') else None
            if chip_num:
                if chip_num not in occurrences:
                    occurrences[chip_num] = {'count': 0, 'attributes': [], 'details': []}
                
                occurrences[chip_num]['count'] += row.occurrence_count
                occurrences[chip_num]['attributes'].append(row.granque_name)
                occurrences[chip_num]['details'].append({
                    'granque': row.granque_name,
                    'count': row.occurrence_count,
                    'denominations': (row.denominations or '').split(',')
                })
                total_draws += row.occurrence_count
        
        return {
            'occurrences': occurrences,
            'total_draws': total_draws,
            'period_info': {
                'start': date_start,
                'end': date_end,
                'universe': universe,
                'marking_type': 'granque'
            }
        }
    
    @staticmethod
    def analyze_temporal_patterns(
        db: Session,
        universe: str,
        tables_config: List[Dict],
        marking_type: str = 'chip'
    ) -> Dict[str, Any]:
        """
        Analyse les patterns temporels sur plusieurs périodes
        
        Args:
            db: Session de base de données
            universe: Nom de l'univers
            tables_config: Configuration des tables (dates, titres, etc.)
            marking_type: Type de marquage
        
        Returns:
            Dict contenant l'analyse complète des patterns
        """
        try:
            # Récupérer les données pour chaque période
            tables_data = []
            for config in tables_config:
                if config.get('type') == 'historical':
                    data = TemporalAnalysisService.get_temporal_data(
                        db, universe, config['dateStart'], config['dateEnd'], marking_type
                    )
                    data.update(config)
                    tables_data.append(data)
            
            # Analyser les patterns
            patterns = TemporalAnalysisService._analyze_patterns(tables_data, marking_type)
            
            return {
                'universe': universe,
                'marking_type': marking_type,
                'tables_data': tables_data,
                'patterns': patterns,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erreur dans analyze_temporal_patterns: {e}")
            return {
                'universe': universe,
                'marking_type': marking_type,
                'tables_data': [],
                'patterns': [],
                'error': str(e)
            }
    
    @staticmethod
    def _analyze_patterns(tables_data: List[Dict], marking_type: str) -> List[Dict]:
        """Analyse les patterns à partir des données temporelles"""
        patterns = []
        
        if len(tables_data) < 2:
            return patterns
        
        # 1. Analyse des récurrences
        recurrence_patterns = TemporalAnalysisService._analyze_recurrence(tables_data)
        patterns.extend(recurrence_patterns)
        
        # 2. Analyse des cycles
        if len(tables_data) >= 3:
            cycle_patterns = TemporalAnalysisService._analyze_cycles(tables_data)
            patterns.extend(cycle_patterns)
        
        # 3. Analyse des séquences
        if len(tables_data) >= 2:
            sequence_patterns = TemporalAnalysisService._analyze_sequences(tables_data)
            patterns.extend(sequence_patterns)
        
        # 4. Analyse spatiale
        spatial_patterns = TemporalAnalysisService._analyze_spatial(tables_data)
        patterns.extend(spatial_patterns)
        
        # 5. Corrélations
        correlation_patterns = TemporalAnalysisService._analyze_correlations(tables_data)
        patterns.extend(correlation_patterns)
        
        return sorted(patterns, key=lambda x: x.get('confidence', 0), reverse=True)
    
    @staticmethod
    def _analyze_recurrence(tables_data: List[Dict]) -> List[Dict]:
        """Analyse les récurrences temporelles"""
        patterns = []
        chip_occurrences = defaultdict(list)
        
        # Collecter les occurrences
        for table in tables_data:
            for chip_num, data in table.get('occurrences', {}).items():
                if data['count'] > 0:
                    chip_occurrences[chip_num].append({
                        'title': table.get('title', ''),
                        'count': data['count'],
                        'attributes': data.get('attributes', [])
                    })
        
        # Analyser les récurrences
        for chip_num, occurrences in chip_occurrences.items():
            if len(occurrences) >= 2:
                total_count = sum(occ['count'] for occ in occurrences)
                consistency = len(occurrences) / len(tables_data)
                intensity = total_count / len(occurrences)
                
                confidence = consistency * 60 + min(intensity * 10, 40)
                
                pattern_type = 'Récurrence Faible'
                if consistency >= 0.8:
                    pattern_type = 'Récurrence Très Forte'
                elif consistency >= 0.6:
                    pattern_type = 'Récurrence Forte'
                elif consistency >= 0.4:
                    pattern_type = 'Récurrence Modérée'
                
                patterns.append({
                    'type': pattern_type,
                    'category': 'Récurrence',
                    'description': f'Chip {chip_num} - Consistance {int(consistency * 100)}%',
                    'details': f'Apparu dans {len(occurrences)}/{len(tables_data)} périodes ({total_count} fois total)',
                    'confidence': min(confidence, 100),
                    'chipNumber': int(chip_num),
                    'data': {
                        'consistency': consistency,
                        'intensity': intensity,
                        'occurrences': [occ['title'] for occ in occurrences]
                    }
                })
        
        return patterns
    
    @staticmethod
    def _analyze_cycles(tables_data: List[Dict]) -> List[Dict]:
        """Analyse les cycles périodiques"""
        patterns = []
        
        for cycle_length in range(2, min(5, len(tables_data))):
            cycle_patterns = TemporalAnalysisService._detect_cycles(tables_data, cycle_length)
            patterns.extend(cycle_patterns)
        
        return patterns
    
    @staticmethod
    def _detect_cycles(tables_data: List[Dict], cycle_length: int) -> List[Dict]:
        """Détecte les cycles d'une longueur donnée"""
        patterns = []
        chip_cycles = defaultdict(list)
        
        # Créer des fenêtres glissantes
        for i in range(len(tables_data) - cycle_length + 1):
            window = tables_data[i:i + cycle_length]
            window_chips = set()
            
            for table in window:
                for chip_num in table.get('occurrences', {}):
                    if table['occurrences'][chip_num]['count'] > 0:
                        window_chips.add(chip_num)
            
            for chip in window_chips:
                chip_cycles[chip].append(i)
        
        # Détecter les cycles réguliers
        for chip, positions in chip_cycles.items():
            if len(positions) >= 2:
                intervals = [positions[i] - positions[i-1] for i in range(1, len(positions))]
                avg_interval = sum(intervals) / len(intervals)
                consistency = sum(1 for i in intervals if abs(i - avg_interval) <= 1) / len(intervals)
                
                if consistency >= 0.7:
                    patterns.append({
                        'type': 'Cycle Périodique',
                        'category': 'Cycle',
                        'description': f'Chip {chip} - Cycle de {cycle_length} périodes',
                        'details': f'Intervalle moyen: {avg_interval:.1f}, Consistance: {int(consistency * 100)}%',
                        'confidence': consistency * 80,
                        'chipNumber': int(chip),
                        'data': {
                            'cycleLength': cycle_length,
                            'avgInterval': avg_interval,
                            'consistency': consistency
                        }
                    })
        
        return patterns
    
    @staticmethod
    def _analyze_sequences(tables_data: List[Dict]) -> List[Dict]:
        """Analyse les séquences et transitions"""
        patterns = []
        transitions = defaultdict(lambda: defaultdict(int))
        
        # Analyser les transitions entre périodes consécutives
        for i in range(len(tables_data) - 1):
            current_chips = set(chip for chip, data in tables_data[i].get('occurrences', {}).items() if data['count'] > 0)
            next_chips = set(chip for chip, data in tables_data[i + 1].get('occurrences', {}).items() if data['count'] > 0)
            
            for chip in current_chips:
                for next_chip in next_chips:
                    if chip != next_chip:
                        transitions[chip][next_chip] += 1
        
        # Identifier les séquences fréquentes
        for chip, followed in transitions.items():
            total_transitions = sum(followed.values())
            for followed_chip, count in followed.items():
                if count >= 2:
                    probability = count / total_transitions
                    patterns.append({
                        'type': 'Séquence Fréquente',
                        'category': 'Séquence',
                        'description': f'Chip {chip} → Chip {followed_chip}',
                        'details': f'Transition observée {count} fois (probabilité: {int(probability * 100)}%)',
                        'confidence': probability * 70 + count * 10,
                        'chipNumber': int(chip),
                        'data': {
                            'followedChip': int(followed_chip),
                            'count': count,
                            'probability': probability
                        }
                    })
        
        return patterns
    
    @staticmethod
    def _analyze_spatial(tables_data: List[Dict]) -> List[Dict]:
        """Analyse spatiale par quadrants"""
        patterns = []
        quadrant_activity = defaultdict(list)
        
        def chip_to_quadrant(chip_num):
            row = (chip_num - 1) // 6 + 1
            col = (chip_num - 1) % 6 + 1
            
            if row <= 4 and col <= 3:
                return 'q1'
            elif row <= 4 and col > 3:
                return 'q2'
            elif row > 4 and col <= 3:
                return 'q3'
            else:
                return 'q4'
        
        # Analyser l'activité par quadrant
        for table in tables_data:
            quadrant_counts = defaultdict(int)
            
            for chip_num, data in table.get('occurrences', {}).items():
                if data['count'] > 0:
                    quadrant = chip_to_quadrant(int(chip_num))
                    quadrant_counts[quadrant] += data['count']
            
            for quadrant in ['q1', 'q2', 'q3', 'q4']:
                quadrant_activity[quadrant].append(quadrant_counts[quadrant])
        
        # Détecter les patterns spatiaux
        for quadrant, activity in quadrant_activity.items():
            avg_activity = sum(activity) / len(activity)
            consistency = sum(1 for a in activity if a > 0) / len(activity)
            
            if avg_activity >= 2 and consistency >= 0.6:
                patterns.append({
                    'type': 'Zone Active',
                    'category': 'Spatial',
                    'description': f'Quadrant {quadrant.upper()} très actif',
                    'details': f'Activité moyenne: {avg_activity:.1f}, Consistance: {int(consistency * 100)}%',
                    'confidence': (avg_activity * 10) + (consistency * 40),
                    'data': {
                        'quadrant': quadrant,
                        'avgActivity': avg_activity,
                        'consistency': consistency
                    }
                })
        
        return patterns
    
    @staticmethod
    def _analyze_correlations(tables_data: List[Dict]) -> List[Dict]:
        """Analyse des corrélations entre chips"""
        patterns = []
        chip_pairs = defaultdict(int)
        
        # Analyser les co-occurrences
        for table in tables_data:
            active_chips = [chip for chip, data in table.get('occurrences', {}).items() if data['count'] > 0]
            
            for i in range(len(active_chips)):
                for j in range(i + 1, len(active_chips)):
                    pair = tuple(sorted([active_chips[i], active_chips[j]]))
                    chip_pairs[pair] += 1
        
        # Identifier les corrélations fortes
        for (chip1, chip2), count in chip_pairs.items():
            if count >= 2:
                correlation = count / len(tables_data)
                
                if correlation >= 0.4:
                    patterns.append({
                        'type': 'Corrélation Forte',
                        'category': 'Corrélation',
                        'description': f'Chips {chip1} et {chip2} apparaissent ensemble',
                        'details': f'Co-occurrence dans {count}/{len(tables_data)} périodes ({int(correlation * 100)}%)',
                        'confidence': correlation * 80,
                        'data': {
                            'chip1': int(chip1),
                            'chip2': int(chip2),
                            'correlation': correlation
                        }
                    })
        
        return patterns