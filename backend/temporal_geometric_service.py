"""
Service d'Analyse Temporelle Géométrique Katula
Implémente l'approche de tracking des zones répétitives en plaçant les résultats 
sur la table de Katula selon leur position géométrique dans le temps.
"""

import psycopg2
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import json
from itertools import combinations
import logging

logger = logging.getLogger(__name__)

class TemporalGeometricService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def analyze_temporal_patterns(self, universe: str, draw_results: List[Dict], 
                                period_config: Dict) -> Dict[str, Any]:
        """
        Analyse les patterns temporels en plaçant les résultats sur la table géométrique
        
        Args:
            universe: Nom de l'univers (mundo, fruity, etc.)
            draw_results: Liste des tirages avec format [80, 72, 89, 50, 26]
            period_config: Configuration des périodes d'analyse
            
        Returns:
            Dict avec les patterns géométriques détectés
        """
        try:
            # 1. Générer toutes les combinaisons 2 à 2 pour chaque tirage
            geometric_mappings = []
            
            for draw in draw_results:
                draw_combinations = self._generate_combinations_from_draw(draw['numbers'])
                draw_mapping = self._map_combinations_to_geometry(
                    universe, draw_combinations, draw['date']
                )
                geometric_mappings.append({
                    'draw_id': draw['id'],
                    'date': draw['date'],
                    'period': draw.get('period', 'unknown'),
                    'combinations': draw_combinations,
                    'geometric_positions': draw_mapping
                })
            
            # 2. Analyser les récurrences géométriques
            recurring_patterns = self._analyze_geometric_recurrence(geometric_mappings)
            
            # 3. Analyser les patterns temporels
            temporal_patterns = self._analyze_temporal_cycles(geometric_mappings, period_config)
            
            # 4. Détecter les zones chaudes
            hot_zones = self._detect_hot_zones(geometric_mappings)
            
            # 5. Générer les prédictions
            predictions = self._generate_geometric_predictions(
                recurring_patterns, temporal_patterns, hot_zones
            )
            
            return {
                'universe': universe,
                'analysis_type': 'temporal_geometric',
                'period_config': period_config,
                'total_draws': len(draw_results),
                'total_combinations': sum(len(m['combinations']) for m in geometric_mappings),
                'geometric_mappings': geometric_mappings,
                'recurring_patterns': recurring_patterns,
                'temporal_patterns': temporal_patterns,
                'hot_zones': hot_zones,
                'predictions': predictions,
                'summary': self._generate_analysis_summary(
                    recurring_patterns, temporal_patterns, hot_zones
                )
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse temporelle géométrique: {e}")
            return {'error': str(e)}
    
    def _generate_combinations_from_draw(self, numbers: List[int]) -> List[Tuple[int, int]]:
        """Génère toutes les combinaisons 2 à 2 d'un tirage"""
        return list(combinations(sorted(numbers), 2))
    
    def _map_combinations_to_geometry(self, universe: str, draw_combinations: List[Tuple], 
                                    draw_date: str) -> List[Dict]:
        """
        Mappe chaque combinaison à sa position géométrique sur la table Katula
        """
        geometric_positions = []
        
        for combo in draw_combinations:
            num1, num2 = combo
            
            # Mode simulation sans BD
            ligne = (num1 % 8) + 1
            colonne = (num2 % 6) + 1
            
            geometric_positions.append({
                'combination': combo,
                'numbers': [num1, num2],
                'chip_id': f"chip{((ligne-1)*6 + colonne)}",
                'denomination': f"combo_{num1}_{num2}",
                'geometric_position': {
                    'ligne': ligne,
                    'colonne': colonne,
                    'coordinates': f"{ligne}{colonne}"
                },
                'attributes': {
                    'tome': f"tome{((num1 + num2) % 4) + 1}",
                    'granque': f"Q{((num1 + num2) % 6) + 1}",
                    'forme': ['carre', 'triangle', 'cercle', 'rectangle'][num1 % 4],
                    'petique': f"petique_{num2 % 3 + 1}"
                },
                'quadrant': self._get_quadrant(ligne, colonne),
                'zone': self._get_geometric_zone(ligne, colonne),
                'draw_date': draw_date,
                'is_simulated': True
            })
        
        return geometric_positions
    
    def _get_quadrant(self, ligne: int, colonne: int) -> str:
        """Détermine le quadrant d'une position"""
        if ligne <= 4 and colonne <= 3:
            return "Q1_top_left"
        elif ligne <= 4 and colonne > 3:
            return "Q2_top_right"
        elif ligne > 4 and colonne <= 3:
            return "Q3_bottom_left"
        else:
            return "Q4_bottom_right"
    
    def _get_geometric_zone(self, ligne: int, colonne: int) -> str:
        """Détermine la zone géométrique"""
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
        
        return f"{v_zone}_{h_zone}"
    
    def _analyze_geometric_recurrence(self, geometric_mappings: List[Dict]) -> List[Dict]:
        """Analyse les récurrences de positions géométriques"""
        position_occurrences = {}
        
        # Compter les occurrences par position
        for mapping in geometric_mappings:
            for pos in mapping['geometric_positions']:
                coord = pos['geometric_position']['coordinates']
                
                if coord not in position_occurrences:
                    position_occurrences[coord] = {
                        'count': 0,
                        'dates': [],
                        'combinations': [],
                        'attributes': [],
                        'quadrant': pos['quadrant'],
                        'zone': pos['zone']
                    }
                
                position_occurrences[coord]['count'] += 1
                position_occurrences[coord]['dates'].append(mapping['date'])
                position_occurrences[coord]['combinations'].append(pos['combination'])
                position_occurrences[coord]['attributes'].append(pos['attributes'])
        
        # Identifier les patterns récurrents
        recurring_patterns = []
        total_mappings = len(geometric_mappings)
        
        for coord, data in position_occurrences.items():
            if data['count'] >= 2:  # Au moins 2 occurrences
                frequency = data['count'] / total_mappings
                
                # Analyser la régularité temporelle
                dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in data['dates']])
                intervals = []
                for i in range(1, len(dates)):
                    interval = (dates[i] - dates[i-1]).days
                    intervals.append(interval)
                
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                interval_consistency = self._calculate_interval_consistency(intervals)
                
                confidence = (frequency * 50) + (interval_consistency * 30) + (data['count'] * 10)
                
                recurring_patterns.append({
                    'type': 'geometric_recurrence',
                    'position': coord,
                    'quadrant': data['quadrant'],
                    'zone': data['zone'],
                    'occurrences': data['count'],
                    'frequency': frequency,
                    'dates': data['dates'],
                    'combinations': data['combinations'],
                    'avg_interval_days': avg_interval,
                    'interval_consistency': interval_consistency,
                    'confidence': min(confidence, 100),
                    'description': f"Position {coord} récurrente {data['count']} fois",
                    'details': f"Fréquence: {frequency:.1%}, Intervalle moyen: {avg_interval:.1f} jours"
                })
        
        return sorted(recurring_patterns, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_interval_consistency(self, intervals: List[int]) -> float:
        """Calcule la consistance des intervalles temporels"""
        if len(intervals) <= 1:
            return 0.0
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # Consistance inversement proportionnelle à l'écart-type
        if avg_interval == 0:
            return 0.0
        
        consistency = max(0, 1 - (std_dev / avg_interval))
        return consistency
    
    def _analyze_temporal_cycles(self, geometric_mappings: List[Dict], 
                                period_config: Dict) -> List[Dict]:
        """Analyse les cycles temporels des positions géométriques"""
        temporal_patterns = []
        
        # Grouper par période si configuré
        if period_config.get('analyze_by_period'):
            period_groups = self._group_by_period(geometric_mappings, period_config)
            
            for period, mappings in period_groups.items():
                period_patterns = self._analyze_period_patterns(period, mappings)
                temporal_patterns.extend(period_patterns)
        
        # Analyser les cycles hebdomadaires/mensuels
        weekly_patterns = self._analyze_weekly_cycles(geometric_mappings)
        monthly_patterns = self._analyze_monthly_cycles(geometric_mappings)
        
        temporal_patterns.extend(weekly_patterns)
        temporal_patterns.extend(monthly_patterns)
        
        return temporal_patterns
    
    def _group_by_period(self, mappings: List[Dict], config: Dict) -> Dict[str, List]:
        """Groupe les mappings par période"""
        groups = {}
        
        for mapping in mappings:
            date = datetime.strptime(mapping['date'], '%Y-%m-%d')
            
            if config.get('period_type') == 'monthly':
                period_key = f"{date.year}-{date.month:02d}"
            elif config.get('period_type') == 'quarterly':
                quarter = (date.month - 1) // 3 + 1
                period_key = f"{date.year}-Q{quarter}"
            else:  # yearly
                period_key = str(date.year)
            
            if period_key not in groups:
                groups[period_key] = []
            groups[period_key].append(mapping)
        
        return groups
    
    def _analyze_period_patterns(self, period: str, mappings: List[Dict]) -> List[Dict]:
        """Analyse les patterns d'une période spécifique"""
        patterns = []
        position_counts = {}
        
        for mapping in mappings:
            for pos in mapping['geometric_positions']:
                coord = pos['geometric_position']['coordinates']
                position_counts[coord] = position_counts.get(coord, 0) + 1
        
        # Identifier les positions dominantes de la période
        total_positions = sum(position_counts.values())
        for coord, count in position_counts.items():
            if count >= 2:  # Au moins 2 occurrences dans la période
                frequency = count / total_positions
                
                patterns.append({
                    'type': 'period_dominance',
                    'period': period,
                    'position': coord,
                    'occurrences': count,
                    'frequency': frequency,
                    'confidence': frequency * 80,
                    'description': f"Position {coord} dominante en {period}",
                    'details': f"{count} occurrences sur {len(mappings)} tirages"
                })
        
        return patterns
    
    def _analyze_weekly_cycles(self, mappings: List[Dict]) -> List[Dict]:
        """Analyse les cycles hebdomadaires"""
        weekly_patterns = []
        weekday_positions = {}
        
        for mapping in mappings:
            date = datetime.strptime(mapping['date'], '%Y-%m-%d')
            weekday = date.weekday()  # 0=Lundi, 6=Dimanche
            
            if weekday not in weekday_positions:
                weekday_positions[weekday] = {}
            
            for pos in mapping['geometric_positions']:
                coord = pos['geometric_position']['coordinates']
                weekday_positions[weekday][coord] = weekday_positions[weekday].get(coord, 0) + 1
        
        # Analyser les patterns par jour de la semaine
        weekday_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for weekday, positions in weekday_positions.items():
            total_day_positions = sum(positions.values())
            
            for coord, count in positions.items():
                if count >= 2:
                    frequency = count / total_day_positions
                    
                    weekly_patterns.append({
                        'type': 'weekly_cycle',
                        'weekday': weekday,
                        'weekday_name': weekday_names[weekday],
                        'position': coord,
                        'occurrences': count,
                        'frequency': frequency,
                        'confidence': frequency * 60,
                        'description': f"Position {coord} fréquente le {weekday_names[weekday]}",
                        'details': f"{count} occurrences les {weekday_names[weekday]}"
                    })
        
        return weekly_patterns
    
    def _analyze_monthly_cycles(self, mappings: List[Dict]) -> List[Dict]:
        """Analyse les cycles mensuels"""
        monthly_patterns = []
        month_positions = {}
        
        for mapping in mappings:
            date = datetime.strptime(mapping['date'], '%Y-%m-%d')
            month = date.month
            
            if month not in month_positions:
                month_positions[month] = {}
            
            for pos in mapping['geometric_positions']:
                coord = pos['geometric_position']['coordinates']
                month_positions[month][coord] = month_positions[month].get(coord, 0) + 1
        
        # Analyser les patterns par mois
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                      'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        for month, positions in month_positions.items():
            total_month_positions = sum(positions.values())
            
            for coord, count in positions.items():
                if count >= 2:
                    frequency = count / total_month_positions
                    
                    monthly_patterns.append({
                        'type': 'monthly_cycle',
                        'month': month,
                        'month_name': month_names[month - 1],
                        'position': coord,
                        'occurrences': count,
                        'frequency': frequency,
                        'confidence': frequency * 70,
                        'description': f"Position {coord} fréquente en {month_names[month - 1]}",
                        'details': f"{count} occurrences en {month_names[month - 1]}"
                    })
        
        return monthly_patterns
    
    def _detect_hot_zones(self, mappings: List[Dict]) -> List[Dict]:
        """Détecte les zones géométriques chaudes"""
        zone_activity = {}
        quadrant_activity = {}
        
        for mapping in mappings:
            for pos in mapping['geometric_positions']:
                zone = pos['zone']
                quadrant = pos['quadrant']
                
                zone_activity[zone] = zone_activity.get(zone, 0) + 1
                quadrant_activity[quadrant] = quadrant_activity.get(quadrant, 0) + 1
        
        hot_zones = []
        total_positions = sum(zone_activity.values())
        
        # Zones chaudes
        for zone, count in zone_activity.items():
            frequency = count / total_positions
            if frequency > 0.15:  # Plus de 15% de l'activité
                hot_zones.append({
                    'type': 'hot_zone',
                    'area_type': 'zone',
                    'area_name': zone,
                    'activity_count': count,
                    'frequency': frequency,
                    'confidence': frequency * 100,
                    'description': f"Zone {zone} très active",
                    'details': f"{count} positions ({frequency:.1%} de l'activité)"
                })
        
        # Quadrants chauds
        total_quadrant_positions = sum(quadrant_activity.values())
        for quadrant, count in quadrant_activity.items():
            frequency = count / total_quadrant_positions
            if frequency > 0.3:  # Plus de 30% de l'activité
                hot_zones.append({
                    'type': 'hot_quadrant',
                    'area_type': 'quadrant',
                    'area_name': quadrant,
                    'activity_count': count,
                    'frequency': frequency,
                    'confidence': frequency * 90,
                    'description': f"Quadrant {quadrant} très actif",
                    'details': f"{count} positions ({frequency:.1%} de l'activité)"
                })
        
        return sorted(hot_zones, key=lambda x: x['confidence'], reverse=True)
    
    def _generate_geometric_predictions(self, recurring_patterns: List[Dict],
                                      temporal_patterns: List[Dict],
                                      hot_zones: List[Dict]) -> List[Dict]:
        """Génère des prédictions basées sur l'analyse géométrique"""
        predictions = []
        
        # Prédictions basées sur les récurrences
        for pattern in recurring_patterns[:5]:  # Top 5
            if pattern['confidence'] >= 70:
                next_occurrence = self._predict_next_occurrence(pattern)
                
                predictions.append({
                    'type': 'geometric_recurrence_prediction',
                    'position': pattern['position'],
                    'quadrant': pattern['quadrant'],
                    'zone': pattern['zone'],
                    'predicted_date': next_occurrence,
                    'confidence': pattern['confidence'] * 0.8,  # Réduction pour incertitude future
                    'basis': 'recurring_pattern',
                    'description': f"Position {pattern['position']} attendue",
                    'details': f"Basé sur récurrence de {pattern['occurrences']} fois"
                })
        
        # Prédictions basées sur les zones chaudes
        for zone in hot_zones[:3]:  # Top 3
            if zone['confidence'] >= 80:
                predictions.append({
                    'type': 'hot_zone_prediction',
                    'area_type': zone['area_type'],
                    'area_name': zone['area_name'],
                    'confidence': zone['confidence'] * 0.7,
                    'basis': 'hot_zone_activity',
                    'description': f"{zone['area_name']} zone à surveiller",
                    'details': f"Activité élevée: {zone['frequency']:.1%}"
                })
        
        # Prédictions temporelles
        current_date = datetime.now()
        weekday = current_date.weekday()
        month = current_date.month
        
        for pattern in temporal_patterns:
            if (pattern['type'] == 'weekly_cycle' and pattern['weekday'] == weekday and 
                pattern['confidence'] >= 60):
                predictions.append({
                    'type': 'temporal_prediction',
                    'position': pattern['position'],
                    'temporal_basis': 'weekly_cycle',
                    'confidence': pattern['confidence'] * 0.6,
                    'description': f"Position {pattern['position']} probable aujourd'hui",
                    'details': f"Pattern hebdomadaire {pattern['weekday_name']}"
                })
            
            elif (pattern['type'] == 'monthly_cycle' and pattern['month'] == month and 
                  pattern['confidence'] >= 65):
                predictions.append({
                    'type': 'temporal_prediction',
                    'position': pattern['position'],
                    'temporal_basis': 'monthly_cycle',
                    'confidence': pattern['confidence'] * 0.65,
                    'description': f"Position {pattern['position']} probable ce mois",
                    'details': f"Pattern mensuel {pattern['month_name']}"
                })
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    
    def _predict_next_occurrence(self, pattern: Dict) -> str:
        """Prédit la prochaine occurrence d'un pattern"""
        if pattern['avg_interval_days'] > 0:
            last_date = datetime.strptime(pattern['dates'][-1], '%Y-%m-%d')
            next_date = last_date + timedelta(days=pattern['avg_interval_days'])
            return next_date.strftime('%Y-%m-%d')
        
        return "indéterminé"
    
    def _generate_analysis_summary(self, recurring_patterns: List[Dict],
                                 temporal_patterns: List[Dict],
                                 hot_zones: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé de l'analyse"""
        return {
            'total_recurring_patterns': len(recurring_patterns),
            'high_confidence_recurrences': len([p for p in recurring_patterns if p['confidence'] >= 80]),
            'total_temporal_patterns': len(temporal_patterns),
            'hot_zones_detected': len(hot_zones),
            'most_active_position': recurring_patterns[0]['position'] if recurring_patterns else None,
            'most_active_zone': hot_zones[0]['area_name'] if hot_zones else None,
            'analysis_quality': self._assess_analysis_quality(recurring_patterns, temporal_patterns),
            'recommendations': self._generate_recommendations(recurring_patterns, hot_zones)
        }
    
    def _assess_analysis_quality(self, recurring_patterns: List[Dict], 
                               temporal_patterns: List[Dict]) -> str:
        """Évalue la qualité de l'analyse"""
        high_conf_recurrences = len([p for p in recurring_patterns if p['confidence'] >= 80])
        total_patterns = len(recurring_patterns) + len(temporal_patterns)
        
        if high_conf_recurrences >= 3 and total_patterns >= 10:
            return "Excellente"
        elif high_conf_recurrences >= 2 and total_patterns >= 5:
            return "Bonne"
        elif total_patterns >= 3:
            return "Acceptable"
        else:
            return "Limitée"
    
    def _generate_recommendations(self, recurring_patterns: List[Dict], 
                                hot_zones: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        if recurring_patterns:
            top_pattern = recurring_patterns[0]
            recommendations.append(
                f"Surveiller la position {top_pattern['position']} "
                f"(confiance: {top_pattern['confidence']:.0f}%)"
            )
        
        if hot_zones:
            top_zone = hot_zones[0]
            recommendations.append(
                f"Concentrer l'attention sur {top_zone['area_name']} "
                f"(activité: {top_zone['frequency']:.1%})"
            )
        
        if len(recurring_patterns) >= 3:
            recommendations.append(
                "Patterns récurrents détectés - analyser les intervalles temporels"
            )
        
        if not recommendations:
            recommendations.append("Collecter plus de données pour améliorer l'analyse")
        
        return recommendations

    def get_temporal_data_for_period(self, universe: str, date_start: str, 
                                   date_end: str, marking_type: str = 'chip') -> Dict[str, Any]:
        """
        Récupère les données temporelles pour une période donnée
        """
        try:
            # Simuler des tirages pour la période
            simulated_draws = self._generate_simulated_draws_for_period(
                date_start, date_end, universe
            )
            
            # Analyser les tirages
            analysis_result = self.analyze_temporal_patterns(
                universe, simulated_draws, {
                    'period_type': 'custom',
                    'date_start': date_start,
                    'date_end': date_end,
                    'analyze_by_period': True
                }
            )
            
            # Adapter au format attendu par l'interface
            occurrences = {}
            
            for mapping in analysis_result.get('geometric_mappings', []):
                for pos in mapping['geometric_positions']:
                    chip_id = pos['chip_id']
                    chip_num = int(chip_id.replace('chip', '')) if 'chip' in str(chip_id) else hash(str(chip_id)) % 48 + 1
                    
                    if chip_num not in occurrences:
                        occurrences[chip_num] = {
                            'count': 0,
                            'attributes': [],
                            'details': []
                        }
                    
                    occurrences[chip_num]['count'] += 1
                    occurrences[chip_num]['attributes'].append(pos['denomination'])
                    occurrences[chip_num]['details'].append({
                        'combination': pos['combination'],
                        'position': pos['geometric_position'],
                        'date': mapping['date']
                    })
            
            return {
                'data': {
                    'occurrences': occurrences,
                    'total_draws': len(simulated_draws),
                    'period_info': {
                        'start_date': date_start,
                        'end_date': date_end,
                        'universe': universe,
                        'marking_type': marking_type
                    },
                    'analysis_summary': analysis_result.get('summary', {}),
                    'patterns_detected': len(analysis_result.get('recurring_patterns', []))
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération données temporelles: {e}")
            return {'error': str(e)}
    
    def _generate_simulated_draws_for_period(self, date_start: str, date_end: str, 
                                           universe: str) -> List[Dict]:
        """Génère des tirages simulés pour une période"""
        import random
        from datetime import datetime, timedelta
        
        start_date = datetime.strptime(date_start, '%Y-%m-%d')
        end_date = datetime.strptime(date_end, '%Y-%m-%d')
        
        draws = []
        current_date = start_date
        draw_id = 1
        
        # Générer un tirage tous les 3-7 jours
        while current_date <= end_date:
            # Générer 5 numéros aléatoires entre 1 et 90
            numbers = sorted(random.sample(range(1, 91), 5))
            
            draws.append({
                'id': f"{universe}_{draw_id}",
                'date': current_date.strftime('%Y-%m-%d'),
                'numbers': numbers,
                'universe': universe
            })
            
            # Avancer de 3 à 7 jours
            current_date += timedelta(days=random.randint(3, 7))
            draw_id += 1
        
        return draws