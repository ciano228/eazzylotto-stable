"""
Service unifié utilisant la table unified_sessions
"""

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class UnifiedDBSessionService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
    
    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """Liste toutes les sessions de la table unifiée"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ws.id, ws.name, ws.description, ws.total_draws, 
                       ws.created_at, ws.is_active, ws.numbers_per_draw,
                       ws.number_range_min, ws.number_range_max,
                       (SELECT COUNT(*) FROM session_draws sd 
                        WHERE sd.session_id = ws.id AND sd.is_completed = true) as completed_draws
                FROM work_sessions ws
                ORDER BY ws.created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                total = row[3] or 0
                completed = row[9] or 0
                progress = round((completed / total * 100)) if total > 0 else 0
                
                sessions.append({
                    'id': row[0],
                    'session_id': row[0],
                    'name': row[1],
                    'session_name': row[1],
                    'description': row[2] or '',
                    'total_draws': total,
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_active': row[5],
                    'numbers_per_draw': row[6] or 5,
                    'number_range_min': row[7] or 1,
                    'number_range_max': row[8] or 90,
                    'completed_draws': completed,
                    'progress_percentage': progress,
                    'status': 'active' if total > 0 else 'empty'
                })
            
            cursor.close()
            conn.close()
            return sessions
            
        except Exception as e:
            print(f'Erreur list_all_sessions: {e}')
            return []
    
    def get_session_draws(self, session_id: int) -> List[Dict[str, Any]]:
        """Récupère uniquement les tirages d'une session"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT draw_number, lottery_name, draw_date, winning_numbers,
                       is_completed, cycle_position, is_no_draw, no_draw_reason
                FROM session_draws 
                WHERE session_id = %s 
                ORDER BY draw_number
            """, (session_id,))
            
            draws = []
            for draw_row in cursor.fetchall():
                draws.append({
                    'draw_number': draw_row[0],
                    'lottery_name': draw_row[1],
                    'draw_date': draw_row[2].strftime('%Y-%m-%d') if draw_row[2] else None,
                    'winning_numbers': draw_row[3] if draw_row[3] else [],
                    'is_completed': draw_row[4],
                    'cycle_position': draw_row[5],
                    'is_no_draw': draw_row[6] if len(draw_row) > 6 else False,
                    'no_draw_reason': draw_row[7] if len(draw_row) > 7 else None
                })
            
            cursor.close()
            conn.close()
            return draws
            
        except Exception as e:
            print(f'Erreur get_session_draws: {e}')
            return []
    
    def create_session(self, session_data: Dict[str, Any]) -> Optional[int]:
        """Crée une nouvelle session"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Créer les tables si elles n'existent pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_sessions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    total_draws INTEGER,
                    numbers_per_draw INTEGER DEFAULT 5,
                    number_range_min INTEGER DEFAULT 1,
                    number_range_max INTEGER DEFAULT 90,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_draws (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES work_sessions(id),
                    draw_number INTEGER,
                    lottery_name VARCHAR(255),
                    draw_date DATE,
                    winning_numbers INTEGER[],
                    is_completed BOOLEAN DEFAULT FALSE,
                    is_no_draw BOOLEAN DEFAULT FALSE,
                    no_draw_reason TEXT,
                    cycle_position INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO work_sessions (
                    name, description, total_draws, numbers_per_draw,
                    number_range_min, number_range_max, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_data.get('name'),
                session_data.get('description', ''),
                session_data.get('total_draws'),
                session_data.get('numbers_per_draw'),
                session_data.get('number_range_min', 1),
                session_data.get('number_range_max', 90),
                True
            ))
            
            session_id = cursor.fetchone()[0]
            
            # Créer les tirages
            schedule = session_data.get('schedule', [])
            for draw_info in schedule:
                cursor.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_name, draw_date,
                        winning_numbers, is_completed, cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    draw_info['draw_number'],
                    draw_info['lottery_name'],
                    draw_info['draw_date'],
                    [],
                    False,
                    draw_info['draw_number']
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return session_id
            
        except Exception as e:
            print(f'Erreur create_session: {e}')
            import traceback
            traceback.print_exc()
            return None
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'une session"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, description, total_draws, numbers_per_draw,
                       number_range_min, number_range_max, created_at
                FROM work_sessions WHERE id = %s
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            draws = self.get_session_draws(session_id)
            
            cursor.close()
            conn.close()
            
            return {
                'id': session_id,
                'name': session_row[0],
                'description': session_row[1],
                'total_draws': session_row[2],
                'numbers_per_draw': session_row[3],
                'number_range_min': session_row[4],
                'number_range_max': session_row[5],
                'created_at': session_row[6].isoformat() if session_row[6] else None,
                'draws': draws
            }
            
        except Exception as e:
            print(f'Erreur get_session: {e}')
            return None
    
    def activate_session(self, session_id: int) -> Dict[str, Any]:
        """Active une session et retourne ses détails complets"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer les détails de la session
            cursor.execute("""
                SELECT name, description, total_draws, numbers_per_draw,
                       number_range_min, number_range_max
                FROM work_sessions WHERE id = %s
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return {'success': False, 'error': 'Session non trouvée'}
            
            # Récupérer les tirages
            draws = self.get_session_draws(session_id)
            
            # Trouver le prochain tirage incomplet
            next_draw = None
            for draw in draws:
                if not draw['is_completed']:
                    next_draw = draw
                    break
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'session': {
                    'id': session_id,
                    'name': session_row[0],
                    'description': session_row[1],
                    'total_draws': session_row[2],
                    'numbers_per_draw': session_row[3],
                    'number_range_min': session_row[4],
                    'number_range_max': session_row[5]
                },
                'draws': draws,
                'next_draw': next_draw
            }
            
        except Exception as e:
            print(f'Erreur activate_session: {e}')
            return {'success': False, 'error': str(e)}
    
    def save_draw_result(self, session_id: int, draw_number: int, draw_data: Dict[str, Any]) -> bool:
        """Sauvegarde ou met à jour un résultat de tirage"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            winning_numbers = draw_data.get('numbers', [])
            is_completed = len(winning_numbers) > 0 and not draw_data.get('is_no_draw', False)
            
            cursor.execute("""
                UPDATE session_draws 
                SET lottery_name = %s,
                    draw_date = %s,
                    winning_numbers = %s,
                    is_completed = %s,
                    is_no_draw = %s,
                    no_draw_reason = %s
                WHERE session_id = %s AND draw_number = %s
            """, (
                draw_data.get('lottery_name', ''),
                draw_data.get('draw_date'),
                winning_numbers,
                is_completed,
                draw_data.get('is_no_draw', False),
                draw_data.get('no_draw_reason'),
                session_id,
                draw_number
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f'ERREUR save_draw_result: {e}')
            return False