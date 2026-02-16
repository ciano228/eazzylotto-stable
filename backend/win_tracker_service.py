"""
Win-Tracker Service - Système de prédiction et analyse de rentabilité des zones
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import psycopg2
from enum import Enum

class ZoneType(Enum):
    PETIQUE = "petique"      # q1, q2, q3, q4
    GRANQUE = "granque"      # Q1, Q2, Q3, Q4, Q5, Q6
    TOME = "tome"            # tome1, tome2, tome3, etc.
    LIGNE = "ligne"          # L1, L2, L3, L4, L5, L6, L7, L8
    COLONNE = "colonne"      # C1, C2, C3, C4, C5, C6
    FORME = "forme"          # carre, triangle, cercle, rectangle

@dataclass
class ZoneAnalysis:
    """Analyse d'une zone de prédiction"""
    zone_type: str
    zone_value: str
    universe: str
    total_combinations: int
    investment_cost: int      # Coût en unités
    potential_gain: int       # Gain potentiel (200 unités)
    net_profit: int          # Bénéfice net
    roi_percentage: float    # Retour sur investissement %
    risk_level: str          # LOW, MEDIUM, HIGH
    recommendation: str      # BUY, HOLD, AVOID
    # Estimations probabilistes
    estimated_probability: float = 0.0
    expected_return: float = 0.0
    expected_profit: float = 0.0
    expected_roi: float = 0.0

@dataclass
class HistoricalResult:
    """Résultat historique pour analyse des tendances"""
    date: datetime
    winning_combination: str
    petique: str
    granque: str
    tome: str
    ligne: int
    colonne: int
    forme: str

class WinTrackerService:
    """Service de prédiction et analyse de rentabilité"""
    
    # Configuration du système
    WINNING_REWARD = 200  # Gain en cas de succès
    UNIT_COST = 1        # Coût par combinaison
    
    # Seuils de risque
    RISK_THRESHOLDS = {
        'LOW': 150,      # Coût <= 150 unités
        'MEDIUM': 180,   # Coût <= 180 unités  
        'HIGH': 200      # Coût > 180 unités
    }
    
    def __init__(self):
        from katula_complete_service import KatulaCompleteService
        self.katula_service = KatulaCompleteService()
        self.db_config = self.katula_service.db_config
    
    def analyze_zone(self, universe: str, zone_type: str, zone_value: str) -> ZoneAnalysis:
        """Analyse complète d'une zone de prédiction"""
        try:
            # Compter les combinaisons dans la zone
            total_combinations = self._count_zone_combinations(universe, zone_type, zone_value)
            
            # Calculs financiers
            investment_cost = total_combinations * self.UNIT_COST
            potential_gain = self.WINNING_REWARD
            # Estimer probabilité que la zone produise au moins une combinaison gagnante
            estimated_p = self._estimate_zone_probability(universe, zone_type, zone_value)

            expected_return = estimated_p * potential_gain
            expected_profit = expected_return - investment_cost
            expected_roi = (expected_profit / investment_cost * 100) if investment_cost > 0 else 0

            # Gain ponctuel sans probabilité (utile pour affichage)
            net_profit = potential_gain - investment_cost
            roi_percentage = (net_profit / investment_cost * 100) if investment_cost > 0 else 0
            
            # Évaluation du risque
            risk_level = self._evaluate_risk(investment_cost)
            # Recommandation basée sur l'espérance (expected_profit) et expected_roi
            recommendation = self._get_recommendation(expected_profit, expected_roi, risk_level)
            
            return ZoneAnalysis(
                zone_type=zone_type,
                zone_value=zone_value,
                universe=universe,
                total_combinations=total_combinations,
                investment_cost=investment_cost,
                potential_gain=potential_gain,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                risk_level=risk_level,
                recommendation=recommendation
            ,estimated_probability=round(estimated_p, 6)
            ,expected_return=round(expected_return, 3)
            ,expected_profit=round(expected_profit, 3)
            ,expected_roi=round(expected_roi, 2)
            )
            
        except Exception as e:
            print(f"[ERROR] analyze_zone: {e}")
            return None
    
    def _count_zone_combinations(self, universe: str, zone_type: str, zone_value: str) -> int:
        """Compte les combinaisons distinctes dans une zone"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Construire la requête selon le type de zone
            if zone_type == "petique":
                where_clause = "petique = %s"
                params = (universe, zone_value)
            elif zone_type == "granque":
                where_clause = "granque_name = %s"
                params = (universe, zone_value)
            elif zone_type == "tome":
                where_clause = "tome = %s"
                params = (universe, zone_value)
            elif zone_type == "ligne":
                ligne_num = int(zone_value.replace('L', ''))
                start_chip = (ligne_num - 1) * 6 + 1
                end_chip = ligne_num * 6
                chip_list = [f"chip{i}" for i in range(start_chip, end_chip + 1)]
                placeholders = ','.join(['%s'] * len(chip_list))
                where_clause = f"chip IN ({placeholders})"
                params = (universe, *chip_list)
            elif zone_type == "colonne":
                col_num = int(zone_value.replace('C', ''))
                chip_list = [f"chip{col_num + i*6}" for i in range(8)]
                placeholders = ','.join(['%s'] * len(chip_list))
                where_clause = f"chip IN ({placeholders})"
                params = (universe, *chip_list)
            elif zone_type == "forme":
                where_clause = "forme = %s"
                params = (universe, zone_value)
            else:
                raise ValueError(f"Type de zone non supporté: {zone_type}")
            
            # Compter les combinaisons distinctes
            cursor.execute(f"""
                SELECT COUNT(DISTINCT combination) 
                FROM combinations 
                WHERE univers = %s AND {where_clause}
            """, params)
            
            count = cursor.fetchone()[0] or 0
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"[ERROR] _count_zone_combinations: {e}")
            return 0
    
    def _evaluate_risk(self, investment_cost: int) -> str:
        """Évalue le niveau de risque basé sur le coût d'investissement"""
        if investment_cost <= self.RISK_THRESHOLDS['LOW']:
            return 'LOW'
        elif investment_cost <= self.RISK_THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _get_recommendation(self, net_profit: int, roi_percentage: float, risk_level: str) -> str:
        """Génère une recommandation d'investissement"""
        if net_profit > 0 and roi_percentage > 5:
            if risk_level == 'LOW':
                return 'BUY'
            elif risk_level == 'MEDIUM':
                return 'BUY' if roi_percentage > 10 else 'HOLD'
            else:  # HIGH risk
                return 'BUY' if roi_percentage > 20 else 'AVOID'
        elif net_profit > 0:
            return 'HOLD'
        else:
            return 'AVOID'

    def _estimate_zone_probability(self, universe: str, zone_type: str, zone_value: str,
                                   lookback: int = 200, decay: float = 0.98, session_id: int = None) -> float:
        """Estime la probabilité qu'une zone produise au moins une combinaison gagnante.

        Méthode POC:
        - Récupère les derniers `lookback` tirages complets depuis `session_draws`.
        - Mappe chaque tirage en positions géométriques via `TemporalGeometricService`.
        - Pour chaque tirage, détecte si au moins une combinaison appartient à la zone.
        - Applique un poids exponentiel décroissant (decay) sur la fenêtre temporelle.
        - Retourne la fréquence pondérée.
        """
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from temporal_geometric_service import TemporalGeometricService

            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            if session_id:
                cur.execute("""
                    SELECT draw_number, draw_date, winning_numbers
                    FROM session_draws
                    WHERE session_id = %s
                      AND winning_numbers IS NOT NULL 
                      AND jsonb_array_length(winning_numbers::jsonb) > 0 
                      AND is_completed = TRUE
                    ORDER BY draw_date DESC
                    LIMIT %s
                """, (session_id, lookback))
            else:
                cur.execute("""
                    SELECT draw_number, draw_date, winning_numbers
                    FROM session_draws
                    WHERE winning_numbers IS NOT NULL 
                      AND jsonb_array_length(winning_numbers::jsonb) > 0 
                      AND is_completed = TRUE
                    ORDER BY draw_date DESC
                    LIMIT %s
                """, (lookback,))
            rows = cur.fetchall()
            conn.close()

            if not rows:
                return 0.0

            # Préparer les tirages pour TemporalGeometricService
            draw_results = []
            for r in rows:
                nums = r.get('winning_numbers')
                # winning_numbers peut être stocké en texte; essayer d'interpréter
                if isinstance(nums, str):
                    try:
                        import json
                        nums_parsed = json.loads(nums)
                    except Exception:
                        # essayer split
                        nums_parsed = [int(x) for x in nums.replace('[','').replace(']','').split(',') if x.strip()]
                else:
                    nums_parsed = nums or []

                # Format date as YYYY-MM-DD only (no time component)
                date_val = r.get('draw_date')
                if hasattr(date_val, 'date'):
                    date_str = date_val.date().isoformat()  # datetime.date only
                elif hasattr(date_val, 'isoformat'):
                    date_str = str(date_val).split('T')[0]  # Strip time if present
                else:
                    date_str = str(date_val).split('T')[0] if date_val else '2024-01-01'

                draw_results.append({'id': r.get('draw_number'), 'date': date_str, 'numbers': nums_parsed})

            tgs = TemporalGeometricService(self.db_config)
            analysis = tgs.analyze_temporal_patterns(universe, draw_results, {'analyze_by_period': False})

            geometric_mappings = analysis.get('geometric_mappings', [])
            if not geometric_mappings:
                return 0.0

            weighted_present = 0.0
            total_weight = 0.0

            # les mappings sont dans l'ordre des draw_results (même ordre)
            for idx, mapping in enumerate(geometric_mappings):
                weight = (decay ** idx)
                total_weight += weight

                found = False
                for pos in mapping.get('geometric_positions', []):
                    attrs = pos.get('attributes', {})
                    # Vérifier selon le type de zone
                    if zone_type == 'petique' and attrs.get('petique'):
                        if str(attrs.get('petique')).lower().endswith(str(zone_value).lower()):
                            found = True
                            break
                    if zone_type == 'granque' and (attrs.get('granque') or pos.get('granque') or attrs.get('granque_name')):
                        granque_val = attrs.get('granque') or attrs.get('granque_name') or pos.get('granque')
                        if granque_val and str(granque_val).lower().endswith(str(zone_value).lower()):
                            found = True
                            break
                    if zone_type == 'tome' and attrs.get('tome'):
                        if str(attrs.get('tome')).lower().endswith(str(zone_value).lower()):
                            found = True
                            break
                    if zone_type == 'ligne' and pos.get('geometric_position'):
                        if str(pos['geometric_position'].get('ligne')) == str(zone_value).replace('L',''):
                            found = True
                            break
                    if zone_type == 'colonne' and pos.get('geometric_position'):
                        if str(pos['geometric_position'].get('colonne')) == str(zone_value).replace('C',''):
                            found = True
                            break
                    if zone_type == 'forme' and attrs.get('forme'):
                        if str(attrs.get('forme')).lower() == str(zone_value).lower():
                            found = True
                            break

                if found:
                    weighted_present += weight

            probability = weighted_present / total_weight if total_weight > 0 else 0.0
            return float(probability)

        except Exception as e:
            print(f"[ERROR] _estimate_zone_probability: {e}")
            return 0.0
    
    def get_all_zones_analysis(self, universe: str) -> List[ZoneAnalysis]:
        """Analyse toutes les zones disponibles pour un univers"""
        analyses = []
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Analyser les pétiques
            for petique in ['q1', 'q2', 'q3', 'q4']:
                analysis = self.analyze_zone(universe, 'petique', petique)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les granques
            cursor.execute("""
                SELECT DISTINCT granque_name 
                FROM combinations 
                WHERE univers = %s AND granque_name IS NOT NULL
            """, (universe,))
            
            for (granque,) in cursor.fetchall():
                analysis = self.analyze_zone(universe, 'granque', granque)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les tomes
            cursor.execute("""
                SELECT DISTINCT tome 
                FROM combinations 
                WHERE univers = %s AND tome IS NOT NULL
            """, (universe,))
            
            for (tome,) in cursor.fetchall():
                analysis = self.analyze_zone(universe, 'tome', tome)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les lignes
            for ligne in range(1, 9):
                analysis = self.analyze_zone(universe, 'ligne', f'L{ligne}')
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les colonnes
            for colonne in range(1, 7):
                analysis = self.analyze_zone(universe, 'colonne', f'C{colonne}')
                if analysis:
                    analyses.append(analysis)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] get_all_zones_analysis: {e}")
        
        # Trier par ROI décroissant
        analyses.sort(key=lambda x: x.roi_percentage, reverse=True)
        return analyses
    
    def get_best_opportunities(self, universe: str, limit: int = 5) -> List[ZoneAnalysis]:
        """Retourne les meilleures opportunités d'investissement"""
        all_analyses = self.get_all_zones_analysis(universe)
        
        # Filtrer seulement les recommandations BUY avec profit positif
        opportunities = [
            analysis for analysis in all_analyses 
            if analysis.recommendation == 'BUY' and analysis.net_profit > 0
        ]
        
        return opportunities[:limit]
    
    def calculate_portfolio_strategy(self, universe: str, budget: int) -> Dict[str, Any]:
        """Calcule une stratégie de portefeuille optimale avec un budget donné"""
        opportunities = self.get_best_opportunities(universe, limit=20)
        
        selected_zones = []
        total_investment = 0
        expected_profit = 0
        
        for opportunity in opportunities:
            if total_investment + opportunity.investment_cost <= budget:
                selected_zones.append(opportunity)
                total_investment += opportunity.investment_cost
                expected_profit += opportunity.net_profit
        
        return {
            'universe': universe,
            'budget': budget,
            'selected_zones': [z.__dict__ for z in selected_zones],
            'total_investment': total_investment,
            'expected_profit': expected_profit,
            'budget_utilization': (total_investment / budget * 100) if budget > 0 else 0,
            'portfolio_roi': (expected_profit / total_investment * 100) if total_investment > 0 else 0
        }
    
    def get_zone_statistics(self, universe: str) -> Dict[str, Any]:
        """Statistiques générales des zones pour un univers"""
        analyses = self.get_all_zones_analysis(universe)
        
        if not analyses:
            return {'error': 'Aucune analyse disponible'}
        
        profitable_zones = [a for a in analyses if a.net_profit > 0]
        buy_recommendations = [a for a in analyses if a.recommendation == 'BUY']
        
        return {
            'universe': universe,
            'total_zones': len(analyses),
            'profitable_zones': len(profitable_zones),
            'buy_recommendations': len(buy_recommendations),
            'average_roi': sum(a.roi_percentage for a in analyses) / len(analyses),
            'best_roi': max(a.roi_percentage for a in analyses),
            'total_combinations': sum(a.total_combinations for a in analyses),
            'risk_distribution': {
                'LOW': len([a for a in analyses if a.risk_level == 'LOW']),
                'MEDIUM': len([a for a in analyses if a.risk_level == 'MEDIUM']),
                'HIGH': len([a for a in analyses if a.risk_level == 'HIGH'])
            }
        }

    
    # Session-specific methods
    def get_best_opportunities_for_session(self, universe: str, session_id: int, limit: int = 5) -> List[ZoneAnalysis]:
        """Retourne les meilleures opportunités pour une session spécifique"""
        all_analyses = self.get_all_zones_analysis_for_session(universe, session_id)
        opportunities = [
            analysis for analysis in all_analyses 
            if analysis.recommendation == 'BUY' and analysis.net_profit > 0
        ]
        return opportunities[:limit]
    
    def get_all_zones_analysis_for_session(self, universe: str, session_id: int) -> List[ZoneAnalysis]:
        """Analyse toutes les zones pour une session spécifique"""
        analyses = []
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Analyser les pétiques
            for petique in ['q1', 'q2', 'q3', 'q4']:
                analysis = self.analyze_zone_for_session(universe, 'petique', petique, session_id)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les granques
            cursor.execute("""
                SELECT DISTINCT granque_name 
                FROM combinations 
                WHERE univers = %s AND granque_name IS NOT NULL
            """, (universe,))
            
            for (granque,) in cursor.fetchall():
                analysis = self.analyze_zone_for_session(universe, 'granque', granque, session_id)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les tomes
            cursor.execute("""
                SELECT DISTINCT tome 
                FROM combinations 
                WHERE univers = %s AND tome IS NOT NULL
            """, (universe,))
            
            for (tome,) in cursor.fetchall():
                analysis = self.analyze_zone_for_session(universe, 'tome', tome, session_id)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les lignes
            for ligne in range(1, 9):
                analysis = self.analyze_zone_for_session(universe, 'ligne', f'L{ligne}', session_id)
                if analysis:
                    analyses.append(analysis)
            
            # Analyser les colonnes
            for colonne in range(1, 7):
                analysis = self.analyze_zone_for_session(universe, 'colonne', f'C{colonne}', session_id)
                if analysis:
                    analyses.append(analysis)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] get_all_zones_analysis_for_session: {e}")
        
        analyses.sort(key=lambda x: x.roi_percentage, reverse=True)
        return analyses
    
    def analyze_zone_for_session(self, universe: str, zone_type: str, zone_value: str, session_id: int) -> ZoneAnalysis:
        """Analyse une zone pour une session spécifique"""
        try:
            total_combinations = self._count_zone_combinations(universe, zone_type, zone_value)
            investment_cost = total_combinations * self.UNIT_COST
            potential_gain = self.WINNING_REWARD
            estimated_p = self._estimate_zone_probability(universe, zone_type, zone_value, session_id=session_id)
            
            expected_return = estimated_p * potential_gain
            expected_profit = expected_return - investment_cost
            expected_roi = (expected_profit / investment_cost * 100) if investment_cost > 0 else 0
            
            net_profit = potential_gain - investment_cost
            roi_percentage = (net_profit / investment_cost * 100) if investment_cost > 0 else 0
            
            risk_level = self._evaluate_risk(investment_cost)
            recommendation = self._get_recommendation(expected_profit, expected_roi, risk_level)
            
            return ZoneAnalysis(
                zone_type=zone_type,
                zone_value=zone_value,
                universe=universe,
                total_combinations=total_combinations,
                investment_cost=investment_cost,
                potential_gain=potential_gain,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                risk_level=risk_level,
                recommendation=recommendation,
                estimated_probability=round(estimated_p, 6),
                expected_return=round(expected_return, 3),
                expected_profit=round(expected_profit, 3),
                expected_roi=round(expected_roi, 2)
            )
        except Exception as e:
            print(f"[ERROR] analyze_zone_for_session: {e}")
            return None
    
    def calculate_portfolio_strategy_for_session(self, universe: str, session_id: int, budget: int) -> Dict[str, Any]:
        """Calcule une stratégie de portefeuille pour une session spécifique"""
        opportunities = self.get_best_opportunities_for_session(universe, session_id, limit=20)
        
        selected_zones = []
        total_investment = 0
        expected_profit = 0
        
        for opportunity in opportunities:
            if total_investment + opportunity.investment_cost <= budget:
                selected_zones.append(opportunity)
                total_investment += opportunity.investment_cost
                expected_profit += opportunity.expected_profit
        
        return {
            'universe': universe,
            'session_id': session_id,
            'budget': budget,
            'selected_zones': [z.__dict__ for z in selected_zones],
            'total_investment': total_investment,
            'expected_profit': expected_profit,
            'budget_utilization': (total_investment / budget * 100) if budget > 0 else 0,
            'portfolio_roi': (expected_profit / total_investment * 100) if total_investment > 0 else 0
        }
    
    def get_zone_statistics_for_session(self, universe: str, session_id: int) -> Dict[str, Any]:
        """Statistiques des zones pour une session spécifique"""
        analyses = self.get_all_zones_analysis_for_session(universe, session_id)
        
        if not analyses:
            return {'error': 'Aucune analyse disponible'}
        
        profitable_zones = [a for a in analyses if a.expected_profit > 0]
        buy_recommendations = [a for a in analyses if a.recommendation == 'BUY']
        
        return {
            'universe': universe,
            'session_id': session_id,
            'total_zones': len(analyses),
            'profitable_zones': len(profitable_zones),
            'buy_recommendations': len(buy_recommendations),
            'average_roi': sum(a.expected_roi for a in analyses) / len(analyses),
            'best_roi': max(a.expected_roi for a in analyses),
            'total_combinations': sum(a.total_combinations for a in analyses),
            'risk_distribution': {
                'LOW': len([a for a in analyses if a.risk_level == 'LOW']),
                'MEDIUM': len([a for a in analyses if a.risk_level == 'MEDIUM']),
                'HIGH': len([a for a in analyses if a.risk_level == 'HIGH'])
            }
        }
