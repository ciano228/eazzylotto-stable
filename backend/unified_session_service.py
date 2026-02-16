"""
Service Unifié de Sessions
Synchronise session_test_001 entre smart-input et katula-temporal-analysis
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

class UnifiedSessionService:
    def __init__(self):
        self.active_session = None
        self.sessions_cache = {}
        self.session_start_date = datetime(2024, 10, 1)  # 01-10-2024 = mardi
        self.loto_schedule = {
            0: 'loto_lundi',    # Lundi
            1: 'loto_mardi',    # Mardi  
            2: 'loto_mercredi', # Mercredi
            3: 'loto_jeudi',    # Jeudi
            4: 'loto_vendredi', # Vendredi
            5: 'loto_samedi',   # Samedi
            6: 'loto_dimanche'  # Dimanche
        }
    
    def initialize_session_test_001(self) -> Dict[str, Any]:
        """Initialise session_test_001 avec dates réelles et périodicité cohérente"""
        
        # Commencer le mardi 01-10-2024 (loto_mardi)
        current_date = self.session_start_date
        draws = []
        
        # Générer 6 périodes complètes (42 tirages)
        for period in range(1, 7):
            period_start_date = current_date
            
            # Générer 7 tirages pour cette période (lundi à dimanche)
            for day_offset in range(7):
                # Calculer la date du tirage
                draw_date = period_start_date + timedelta(days=day_offset)
                day_of_week = draw_date.weekday()  # 0=lundi, 6=dimanche
                
                draw_number = (period - 1) * 7 + day_offset + 1
                draw_id = f"session_test_001_P{period:02d}_{self.loto_schedule[day_of_week]}"
                
                # Tous les tirages sont complétés pour l'analyse
                is_completed = True
                
                # Générer des numéros cohérents basés sur la date
                seed = int(draw_date.strftime('%Y%m%d'))
                random.seed(seed)
                numbers = sorted(random.sample(range(1, 91), 5))
                
                # Fin de période = lundi (jour précédant le mardi de début)
                is_period_end = (day_of_week == 0 and day_offset > 0)  # Lundi = fin de période
                
                draws.append({
                    'id': draw_id,
                    'draw_number': draw_number,
                    'period': period,
                    'loto_name': self.loto_schedule[day_of_week],
                    'draw_date': draw_date.strftime('%Y-%m-%d'),
                    'day_of_week': day_of_week,
                    'numbers': numbers,
                    'is_completed': is_completed,
                    'is_period_end': is_period_end
                })
            
            # Passer à la semaine suivante
            current_date += timedelta(days=7)
        
        session_data = {
            'session_name': 'session_test_001',
            'periods': 6,
            'loto_names': list(self.loto_schedule.values()),
            'draws': draws,
            'total_draws': 42,
            'completed_draws': 42,
            'current_draw': 43,
            'progress_percentage': 100.0,
            'created_at': self.session_start_date.strftime('%Y-%m-%d'),
            'start_date': self.session_start_date.strftime('%Y-%m-%d'),
            'metadata': {
                'universe': 'mundo',
                'numbers_per_draw': 5,
                'number_range_min': 1,
                'number_range_max': 90,
                'cycle_type': 'weekly',
                'period_duration': 7
            }
        }
        
        # Mettre en cache
        self.sessions_cache['session_test_001'] = session_data
        self.active_session = 'session_test_001'
        
        return session_data
    
    def get_session_for_smart_input(self, session_name: str = 'session_test_001') -> Dict[str, Any]:
        """Format session pour smart-input.html"""
        
        if session_name not in self.sessions_cache:
            self.initialize_session_test_001()
        
        session = self.sessions_cache[session_name]
        
        # Format pour smart-input
        return {
            'session_name': session['session_name'],
            'name': session['session_name'],
            'periods': session['periods'],
            'total_draws': session['total_draws'],
            'completed_draws': session['completed_draws'],
            'progress_percentage': session['progress_percentage'],
            'created_at': session['created_at'],
            'start_date': session['start_date'],
            'metadata': session['metadata'],
            'is_active': True,
            'draws': session['draws']
        }
    
    def get_session_for_temporal_analysis(self, session_name: str = 'session_test_001') -> Dict[str, Any]:
        """Format session pour katula-temporal-analysis.html"""
        
        if session_name not in self.sessions_cache:
            self.initialize_session_test_001()
        
        session = self.sessions_cache[session_name]
        
        # Convertir au format attendu par l'analyse temporelle
        formatted_draws = []
        for draw in session['draws']:
            formatted_draws.append({
                'id': draw['id'],
                'date': draw['draw_date'],
                'draw_date': draw['draw_date'],
                'numbers': draw['numbers'],
                'universe': session['metadata']['universe'],
                'loto_name': draw['loto_name'],
                'period': draw['period'],
                'is_completed': draw['is_completed']
            })
        
        return {
            'session_name': session['session_name'],
            'draws': formatted_draws,
            'periods': session['periods'],
            'loto_names': session['loto_names']
        }
    
    def get_current_draw(self, session_name: str = 'session_test_001') -> Optional[Dict[str, Any]]:
        """Récupère le tirage courant avec dates réelles"""
        
        if session_name not in self.sessions_cache:
            self.initialize_session_test_001()
        
        session = self.sessions_cache[session_name]
        
        # Trouver le premier tirage non complété
        for draw in session['draws']:
            if not draw['is_completed']:
                return {
                    'draw_id': draw['id'],
                    'draw_number': draw['draw_number'],
                    'loto_name': draw['loto_name'],
                    'draw_date': draw['draw_date'],
                    'period': draw['period'],
                    'day_of_week': draw['day_of_week'],
                    'is_completed': False,
                    'numbers': [],
                    'is_period_end': draw.get('is_period_end', False)
                }
        
        # Si tous complétés, retourner null (session terminée)
        return None
        
        return None
    
    def save_draw(self, session_name: str, draw_data: Dict[str, Any]) -> bool:
        """Sauvegarde un tirage dans la session"""
        
        if session_name not in self.sessions_cache:
            return False
        
        session = self.sessions_cache[session_name]
        
        # Trouver et mettre à jour le tirage
        for draw in session['draws']:
            if draw['id'] == draw_data['draw_id']:
                draw['numbers'] = draw_data['numbers']
                draw['is_completed'] = True
                break
        
        # Mettre à jour les statistiques
        session['completed_draws'] = len([d for d in session['draws'] if d['is_completed']])
        session['progress_percentage'] = (session['completed_draws'] / session['total_draws']) * 100
        session['current_draw'] = session['completed_draws'] + 1
        
        return True
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Liste toutes les sessions disponibles"""
        
        # S'assurer que session_test_001 existe
        if 'session_test_001' not in self.sessions_cache:
            self.initialize_session_test_001()
        
        sessions = []
        for session_name, session_data in self.sessions_cache.items():
            sessions.append({
                'name': session_data['session_name'],
                'periods': session_data['periods'],
                'total_draws': session_data['total_draws'],
                'completed_draws': session_data['completed_draws'],
                'progress_percentage': session_data['progress_percentage'],
                'created_at': session_data['created_at'],
                'metadata': session_data['metadata'],
                'is_active': session_name == self.active_session
            })
        
        return sessions
    
    def get_session_progress(self, session_name: str) -> Dict[str, Any]:
        """Récupère le progrès d'une session"""
        
        if session_name not in self.sessions_cache:
            if session_name == 'session_test_001':
                self.initialize_session_test_001()
            else:
                return {'error': 'Session non trouvée'}
        
        session = self.sessions_cache[session_name]
        
        return {
            'session_name': session_name,
            'current_draw': session['current_draw'],
            'total_draws': session['total_draws'],
            'completed_draws': session['completed_draws'],
            'progress_percentage': session['progress_percentage'],
            'remaining_draws': session['total_draws'] - session['completed_draws']
        }

# Instance globale
unified_session_service = UnifiedSessionService()