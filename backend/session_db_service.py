"""
Service de Gestion des Sessions en Base de Données
Gère les sessions réelles incluant session_test_001
"""

import psycopg2
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class SessionDBService:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_db = bool(db_config and db_config.get('host'))
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions disponibles"""
        if not self.use_db:
            return self._get_mock_sessions()
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ts.session_name, ts.periods, ts.created_at, ts.metadata,
                       COUNT(td.id) as total_draws,
                       COUNT(CASE WHEN td.numbers IS NOT NULL THEN 1 END) as completed_draws
                FROM test_sessions_real ts
                LEFT JOIN test_draws_real td ON ts.id = td.session_id
                GROUP BY ts.session_name, ts.periods, ts.created_at, ts.metadata
                ORDER BY ts.created_at DESC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            sessions = []
            for result in results:
                session_name, periods, created_at, metadata, total_draws, completed_draws = result
                
                sessions.append({
                    'name': session_name,
                    'periods': periods,
                    'total_draws': total_draws,
                    'completed_draws': completed_draws,
                    'progress_percentage': (completed_draws / total_draws * 100) if total_draws > 0 else 0,
                    'created_at': created_at.strftime('%Y-%m-%d') if created_at else None,
                    'metadata': metadata or {},
                    'is_active': session_name == 'session_test_001'
                })
            
            return sessions
            
        except Exception as e:
            print(f"Erreur récupération sessions: {e}")
            return self._get_mock_sessions()
    
    def get_session_details(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'une session spécifique"""
        if not self.use_db:
            return self._get_mock_session_details(session_name)
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer les infos de session
            cursor.execute("""
                SELECT session_name, periods, metadata, created_at
                FROM test_sessions_real
                WHERE session_name = %s
            """, (session_name,))
            
            session_result = cursor.fetchone()
            if not session_result:
                return None
            
            session_name, periods, metadata, created_at = session_result
            
            # Récupérer les tirages
            cursor.execute("""
                SELECT draw_id, period, loto_name, draw_date, day_of_week, numbers
                FROM test_draws_real td
                JOIN test_sessions_real ts ON td.session_id = ts.id
                WHERE ts.session_name = %s
                ORDER BY period, day_of_week
            """, (session_name,))
            
            draws_results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            draws = []
            for draw_result in draws_results:
                draw_id, period, loto_name, draw_date, day_of_week, numbers = draw_result
                
                draws.append({
                    'id': draw_id,
                    'period': period,
                    'loto_name': loto_name,
                    'draw_date': draw_date.strftime('%Y-%m-%d') if draw_date else None,
                    'day_of_week': day_of_week,
                    'numbers': numbers or [],
                    'is_completed': bool(numbers and len(numbers) > 0)
                })
            
            return {
                'session_name': session_name,
                'periods': periods,
                'metadata': metadata or {},
                'created_at': created_at.strftime('%Y-%m-%d') if created_at else None,
                'draws': draws,
                'total_draws': len(draws),
                'completed_draws': len([d for d in draws if d['is_completed']]),
                'current_draw': self._get_current_draw_number(draws)
            }
            
        except Exception as e:
            print(f"Erreur récupération session {session_name}: {e}")
            return self._get_mock_session_details(session_name)
    
    def get_session_progress(self, session_name: str) -> Dict[str, Any]:
        """Récupère le progrès d'une session"""
        session_details = self.get_session_details(session_name)
        
        if not session_details:
            return {'error': 'Session non trouvée'}
        
        total_draws = session_details['total_draws']
        completed_draws = session_details['completed_draws']
        current_draw = session_details['current_draw']
        
        return {
            'session_name': session_name,
            'current_draw': current_draw,
            'total_draws': total_draws,
            'completed_draws': completed_draws,
            'progress_percentage': (completed_draws / total_draws * 100) if total_draws > 0 else 0,
            'remaining_draws': total_draws - completed_draws
        }
    
    def get_current_draw_data(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les données du tirage courant"""
        session_details = self.get_session_details(session_name)
        
        if not session_details:
            return None
        
        # Trouver le premier tirage non complété
        for draw in session_details['draws']:
            if not draw['is_completed']:
                return {
                    'draw_id': draw['id'],
                    'draw_number': draw['period'] * 7 + draw['day_of_week'],  # Calcul approximatif
                    'loto_name': draw['loto_name'],
                    'draw_date': draw['draw_date'],
                    'period': draw['period'],
                    'day_of_week': draw['day_of_week'],
                    'is_completed': False,
                    'numbers': []
                }
        
        # Si tous sont complétés, retourner le dernier
        if session_details['draws']:
            last_draw = session_details['draws'][-1]
            return {
                'draw_id': last_draw['id'],
                'draw_number': len(session_details['draws']),
                'loto_name': last_draw['loto_name'],
                'draw_date': last_draw['draw_date'],
                'period': last_draw['period'],
                'day_of_week': last_draw['day_of_week'],
                'is_completed': True,
                'numbers': last_draw['numbers']
            }
        
        return None
    
    def save_draw_result(self, session_name: str, draw_data: Dict[str, Any]) -> bool:
        """Sauvegarde le résultat d'un tirage"""
        if not self.use_db:
            print(f"Mode simulation - Tirage sauvegardé: {draw_data}")
            return True
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Mettre à jour le tirage
            cursor.execute("""
                UPDATE test_draws_real 
                SET numbers = %s
                WHERE draw_id = %s
            """, (draw_data['numbers'], draw_data['draw_id']))
            
            # Sauvegarder aussi les combinaisons géométriques
            self._save_draw_combinations(cursor, draw_data)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde tirage: {e}")
            return False
    
    def _save_draw_combinations(self, cursor, draw_data: Dict[str, Any]):
        """Sauvegarde les combinaisons géométriques d'un tirage"""
        from itertools import combinations
        
        numbers = draw_data['numbers']
        draw_id = draw_data['draw_id']
        
        # Supprimer les anciennes combinaisons
        cursor.execute("""
            DELETE FROM geometric_combinations_real 
            WHERE draw_id = %s
        """, (draw_id,))
        
        # Générer et sauvegarder les nouvelles combinaisons
        combos = list(combinations(numbers, 2))
        
        for combo in combos:
            num1, num2 = combo
            
            # Calculer la position géométrique
            ligne = (num1 % 8) + 1
            colonne = (num2 % 6) + 1
            
            # Calculer les attributs
            quadrant = self._get_quadrant(ligne, colonne)
            zone = self._get_zone(ligne, colonne)
            tome = f"tome{((num1 + num2) % 4) + 1}"
            granque = f"Q{((num1 + num2) % 6) + 1}"
            forme = ['carre', 'triangle', 'cercle', 'rectangle'][num1 % 4]
            
            cursor.execute("""
                INSERT INTO geometric_combinations_real 
                (draw_id, combination_numbers, geometric_position, ligne, colonne, 
                 quadrant, zone, tome, granque, forme)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                draw_id,
                [num1, num2],
                f"{ligne}{colonne}",
                ligne,
                colonne,
                quadrant,
                zone,
                tome,
                granque,
                forme
            ))
    
    def _get_current_draw_number(self, draws: List[Dict]) -> int:
        """Calcule le numéro du tirage courant"""
        completed_count = len([d for d in draws if d['is_completed']])
        return completed_count + 1
    
    def _get_mock_sessions(self) -> List[Dict[str, Any]]:
        """Sessions simulées pour les tests"""
        return [
            {
                'name': 'session_test_001',
                'periods': 6,
                'total_draws': 42,
                'completed_draws': 15,
                'progress_percentage': 35.7,
                'created_at': '2024-01-01',
                'metadata': {'loto_names': ['loto_lundi', 'loto_mardi', 'loto_mercredi', 'loto_jeudi', 'loto_vendredi', 'loto_samedi', 'loto_dimanche']},
                'is_active': True
            },
            {
                'name': 'session_janvier_2025',
                'periods': 4,
                'total_draws': 28,
                'completed_draws': 8,
                'progress_percentage': 28.6,
                'created_at': '2025-01-01',
                'metadata': {},
                'is_active': False
            }
        ]
    
    def _get_mock_session_details(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Détails de session simulés"""
        if session_name == 'session_test_001':
            # Générer 42 tirages (6 périodes × 7 jours)
            draws = []
            loto_names = ['loto_lundi', 'loto_mardi', 'loto_mercredi', 'loto_jeudi', 'loto_vendredi', 'loto_samedi', 'loto_dimanche']
            
            for period in range(1, 7):  # 6 périodes
                for day in range(7):  # 7 jours
                    draw_id = f"session_test_001_P{period}_{loto_names[day]}"
                    
                    # Simuler quelques tirages complétés
                    is_completed = (period - 1) * 7 + day < 15
                    numbers = []
                    
                    if is_completed:
                        # Générer des numéros aléatoires pour les tirages complétés
                        import random
                        random.seed((period * 7 + day) * 42)  # Seed fixe pour reproductibilité
                        numbers = sorted(random.sample(range(1, 91), 5))
                    
                    draws.append({
                        'id': draw_id,
                        'period': period,
                        'loto_name': loto_names[day],
                        'draw_date': f"2024-01-{(period-1)*7 + day + 1:02d}",
                        'day_of_week': day + 1,
                        'numbers': numbers,
                        'is_completed': is_completed
                    })
            
            return {
                'session_name': 'session_test_001',
                'periods': 6,
                'metadata': {'loto_names': loto_names},
                'created_at': '2024-01-01',
                'draws': draws,
                'total_draws': 42,
                'completed_draws': 15,
                'current_draw': 16
            }
        
        return None
    
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
    
    def _get_zone(self, ligne: int, colonne: int) -> str:
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