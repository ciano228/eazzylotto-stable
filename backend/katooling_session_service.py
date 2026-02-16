#!/usr/bin/env python3
"""
Service pour accéder aux sessions dans katooling_main_system
"""

import psycopg2
import json
from datetime import datetime

class KatoolingSessionService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
    
    def get_connection(self):
        """Obtenir une connexion à la base"""
        return psycopg2.connect(**self.db_config)
    
    def get_all_sessions(self):
        """Récupérer toutes les sessions disponibles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sessions = []
            
            # Sessions work_sessions
            cursor.execute("""
                SELECT id, name, description, lottery_type, total_draws, current_draw, is_active
                FROM work_sessions
                ORDER BY id
            """)
            work_sessions = cursor.fetchall()
            
            for session in work_sessions:
                session_id, name, desc, lottery_type, total_draws, current_draw, is_active = session
                
                # Compter les tirages réels
                cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
                actual_draws = cursor.fetchone()[0]
                
                sessions.append({
                    'id': f'work_{session_id}',
                    'real_id': session_id,
                    'name': name,
                    'description': desc or '',
                    'type': 'work_session',
                    'lottery_type': lottery_type,
                    'total_draws': total_draws or 0,
                    'current_draw': current_draw or 0,
                    'actual_draws': actual_draws,
                    'is_active': is_active,
                    'progress': (actual_draws / max(total_draws, 1)) * 100 if total_draws else 0
                })
            
            # Sessions unified_sessions
            cursor.execute("""
                SELECT id, session_uuid, name, description, session_type, lottery_type, 
                       numbers_per_draw, total_draws
                FROM unified_sessions
                ORDER BY id
            """)
            unified_sessions = cursor.fetchall()
            
            for session in unified_sessions:
                session_id, uuid, name, desc, session_type, lottery_type, numbers_per_draw, total_draws = session
                
                # Compter les tirages réels
                cursor.execute("SELECT COUNT(*) FROM unified_draws WHERE session_uuid = %s", (uuid,))
                actual_draws = cursor.fetchone()[0]
                
                sessions.append({
                    'id': f'unified_{session_id}',
                    'real_id': uuid,
                    'name': name,
                    'description': desc or '',
                    'type': 'unified_session',
                    'session_type': session_type,
                    'lottery_type': lottery_type,
                    'numbers_per_draw': numbers_per_draw,
                    'total_draws': total_draws or 0,
                    'actual_draws': actual_draws,
                    'progress': (actual_draws / max(total_draws, 1)) * 100 if total_draws else 0
                })
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'success',
                'sessions': sessions,
                'total_sessions': len(sessions)
            }
            
        except Exception as e:
            cursor.close()
            conn.close()
            return {
                'status': 'error',
                'error': str(e),
                'sessions': []
            }
    
    def get_session_details(self, session_id):
        """Récupérer les détails d'une session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Déterminer le type de session
            if session_id.startswith('work_'):
                real_id = int(session_id.replace('work_', ''))
                return self._get_work_session_details(cursor, real_id)
            elif session_id.startswith('unified_'):
                real_id = int(session_id.replace('unified_', ''))
                return self._get_unified_session_details(cursor, real_id)
            else:
                # Essayer de trouver par nom
                return self._get_session_by_name(cursor, session_id)
                
        except Exception as e:
            cursor.close()
            conn.close()
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_work_session_details(self, cursor, session_id):
        """Détails d'une work_session"""
        cursor.execute("""
            SELECT id, name, description, lottery_type, numbers_per_draw, 
                   number_range_min, number_range_max, total_draws, current_draw, is_active
            FROM work_sessions
            WHERE id = %s
        """, (session_id,))
        
        session_data = cursor.fetchone()
        if not session_data:
            return {'status': 'error', 'error': 'Session non trouvée'}
        
        # Récupérer les tirages
        cursor.execute("""
            SELECT id, draw_number, lottery_name, draw_date, winning_numbers, 
                   is_completed, cycle_position, is_no_draw
            FROM session_draws
            WHERE session_id = %s
            ORDER BY draw_number
        """, (session_id,))
        
        draws = cursor.fetchall()
        
        # Formater les données
        session_info = {
            'id': session_data[0],
            'name': session_data[1],
            'description': session_data[2] or '',
            'lottery_type': session_data[3],
            'numbers_per_draw': session_data[4] or 5,
            'number_range_min': session_data[5] or 1,
            'number_range_max': session_data[6] or 90,
            'total_draws': session_data[7] or 0,
            'current_draw': session_data[8] or 0,
            'is_active': session_data[9],
            'type': 'work_session'
        }
        
        # Formater les tirages
        formatted_draws = []
        for draw in draws:
            draw_id, draw_number, lottery_name, draw_date, winning_numbers, is_completed, cycle_position, is_no_draw = draw
            
            # Parser les numéros gagnants
            numbers = []
            if winning_numbers:
                if isinstance(winning_numbers, str):
                    try:
                        numbers = json.loads(winning_numbers)
                    except:
                        numbers = []
                elif isinstance(winning_numbers, list):
                    numbers = winning_numbers
            
            formatted_draws.append({
                'id': draw_id,
                'draw_number': draw_number,
                'lottery_name': lottery_name,
                'draw_date': draw_date.isoformat() if draw_date else None,
                'numbers': numbers,
                'is_completed': is_completed,
                'cycle_position': cycle_position,
                'is_no_draw': is_no_draw
            })
        
        return {
            'status': 'success',
            'session': session_info,
            'draws': formatted_draws,
            'total_draws': len(formatted_draws),
            'completed_draws': len([d for d in formatted_draws if d['is_completed']])
        }
    
    def _get_unified_session_details(self, cursor, session_id):
        """Détails d'une unified_session"""
        cursor.execute("""
            SELECT id, session_uuid, name, description, session_type, lottery_type,
                   numbers_per_draw, number_range_min, number_range_max, total_draws
            FROM unified_sessions
            WHERE id = %s
        """, (session_id,))
        
        session_data = cursor.fetchone()
        if not session_data:
            return {'status': 'error', 'error': 'Session non trouvée'}
        
        session_uuid = session_data[1]
        
        # Récupérer les tirages
        cursor.execute("""
            SELECT id, draw_number, lottery_name, draw_date, winning_numbers, 
                   is_completed, metadata
            FROM unified_draws
            WHERE session_uuid = %s
            ORDER BY draw_number
        """, (session_uuid,))
        
        draws = cursor.fetchall()
        
        # Formater les données
        session_info = {
            'id': session_data[0],
            'uuid': session_uuid,
            'name': session_data[2],
            'description': session_data[3] or '',
            'session_type': session_data[4],
            'lottery_type': session_data[5],
            'numbers_per_draw': session_data[6] or 5,
            'number_range_min': session_data[7] or 1,
            'number_range_max': session_data[8] or 90,
            'total_draws': session_data[9] or 0,
            'type': 'unified_session'
        }
        
        # Formater les tirages
        formatted_draws = []
        for draw in draws:
            draw_id, draw_number, lottery_name, draw_date, winning_numbers, is_completed, metadata = draw
            
            # Parser les numéros gagnants
            numbers = []
            if winning_numbers:
                if isinstance(winning_numbers, str):
                    try:
                        numbers = json.loads(winning_numbers)
                    except:
                        numbers = []
                elif isinstance(winning_numbers, list):
                    numbers = winning_numbers
            
            formatted_draws.append({
                'id': draw_id,
                'draw_number': draw_number,
                'lottery_name': lottery_name,
                'draw_date': draw_date.isoformat() if draw_date else None,
                'numbers': numbers,
                'is_completed': is_completed,
                'metadata': metadata
            })
        
        return {
            'status': 'success',
            'session': session_info,
            'draws': formatted_draws,
            'total_draws': len(formatted_draws),
            'completed_draws': len([d for d in formatted_draws if d['is_completed']])
        }
    
    def _get_session_by_name(self, cursor, session_name):
        """Chercher une session par nom"""
        # Chercher dans work_sessions
        cursor.execute("SELECT id FROM work_sessions WHERE name = %s", (session_name,))
        work_result = cursor.fetchone()
        
        if work_result:
            return self._get_work_session_details(cursor, work_result[0])
        
        # Chercher dans unified_sessions
        cursor.execute("SELECT id FROM unified_sessions WHERE name = %s", (session_name,))
        unified_result = cursor.fetchone()
        
        if unified_result:
            return self._get_unified_session_details(cursor, unified_result[0])
        
        return {'status': 'error', 'error': f'Session {session_name} non trouvée'}
    
    def get_algeria_sessions(self):
        """Récupérer spécifiquement les sessions Algeria"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            algeria_sessions = []
            
            # Chercher dans work_sessions
            cursor.execute("""
                SELECT id, name, description, lottery_type, total_draws, current_draw
                FROM work_sessions
                WHERE name ILIKE '%algeria%'
                ORDER BY id
            """)
            
            work_algeria = cursor.fetchall()
            for session in work_algeria:
                session_id, name, desc, lottery_type, total_draws, current_draw = session
                
                # Compter les tirages
                cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
                actual_draws = cursor.fetchone()[0]
                
                algeria_sessions.append({
                    'id': f'work_{session_id}',
                    'real_id': session_id,
                    'name': name,
                    'description': desc or '',
                    'type': 'work_session',
                    'lottery_type': lottery_type,
                    'total_draws': total_draws or 0,
                    'actual_draws': actual_draws,
                    'access_key': f'work_{session_id}'
                })
            
            # Chercher dans unified_sessions
            cursor.execute("""
                SELECT id, session_uuid, name, description, session_type, total_draws
                FROM unified_sessions
                WHERE name ILIKE '%algeria%'
                ORDER BY id
            """)
            
            unified_algeria = cursor.fetchall()
            for session in unified_algeria:
                session_id, uuid, name, desc, session_type, total_draws = session
                
                # Compter les tirages
                cursor.execute("SELECT COUNT(*) FROM unified_draws WHERE session_uuid = %s", (uuid,))
                actual_draws = cursor.fetchone()[0]
                
                algeria_sessions.append({
                    'id': f'unified_{session_id}',
                    'real_id': uuid,
                    'name': name,
                    'description': desc or '',
                    'type': 'unified_session',
                    'session_type': session_type,
                    'total_draws': total_draws or 0,
                    'actual_draws': actual_draws,
                    'access_key': f'unified_{session_id}'
                })
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'success',
                'algeria_sessions': algeria_sessions,
                'total_found': len(algeria_sessions)
            }
            
        except Exception as e:
            cursor.close()
            conn.close()
            return {
                'status': 'error',
                'error': str(e),
                'algeria_sessions': []
            }

def test_service():
    """Tester le service"""
    service = KatoolingSessionService()
    
    print("Test du service KatoolingSessionService...")
    
    # 1. Lister toutes les sessions
    print("\n1. Toutes les sessions:")
    all_sessions = service.get_all_sessions()
    if all_sessions['status'] == 'success':
        for session in all_sessions['sessions']:
            print(f"  - {session['id']}: {session['name']} ({session['actual_draws']} tirages)")
    else:
        print(f"  Erreur: {all_sessions['error']}")
    
    # 2. Sessions Algeria spécifiquement
    print("\n2. Sessions Algeria:")
    algeria_sessions = service.get_algeria_sessions()
    if algeria_sessions['status'] == 'success':
        for session in algeria_sessions['algeria_sessions']:
            print(f"  - {session['access_key']}: {session['name']} ({session['actual_draws']} tirages)")
            
            # Tester l'accès aux détails
            details = service.get_session_details(session['access_key'])
            if details['status'] == 'success':
                print(f"    Détails OK: {details['completed_draws']}/{details['total_draws']} tirages complétés")
            else:
                print(f"    Erreur détails: {details['error']}")
    else:
        print(f"  Erreur: {algeria_sessions['error']}")

if __name__ == "__main__":
    test_service()