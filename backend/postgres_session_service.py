from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json
from .migration_service import MigrationService

class PostgresSessionService:
    def __init__(self):
        self.migration_service = MigrationService()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session depuis PostgreSQL"""
        try:
            import psycopg2
            
            # Extraire l'ID numérique
            if session_id.startswith('work_'):
                numeric_id = int(session_id.replace('work_', ''))
            else:
                numeric_id = int(session_id)
            
            conn = psycopg2.connect(
                host='localhost',
                database='katooling_main_system',
                user='postgres', 
                password='Katulaa_33',
                port=5432
            )
            cursor = conn.cursor()
            
            # Récupérer la session
            cursor.execute("""
                SELECT id, name, description, created_at, total_draws
                FROM work_sessions WHERE id = %s
            """, (numeric_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # Récupérer les tirages
            cursor.execute("""
                SELECT draw_number, lottery_name, draw_date, winning_numbers
                FROM session_draws 
                WHERE session_id = %s 
                ORDER BY draw_number
            """, (numeric_id,))
            
            draws_rows = cursor.fetchall()
            
            # Construire la structure
            session_data = {
                'session_id': session_id,
                'name': session_row[1] or f'Session {session_row[0]}',
                'description': session_row[2] or '',
                'created_at': session_row[3].isoformat() if session_row[3] else None,
                'total_draws': len(draws_rows),
                'draws': []
            }
            
            for draw_row in draws_rows:
                session_data['draws'].append({
                    'draw_number': draw_row[0],
                    'lottery_name': draw_row[1],
                    'date': draw_row[2].strftime('%Y-%m-%d') if draw_row[2] else None,
                    'numbers': draw_row[3] if draw_row[3] else []
                })
            
            cursor.close()
            conn.close()
            return session_data
            
        except Exception as e:
            print(f'Erreur get_session: {e}')
            return None
    
    def create_session(self, session_id: str, session_name: str = None) -> bool:
        """Crée une nouvelle session"""
        name = session_name or session_id
        return self.migration_service.create_session_in_postgres(session_id, name)
    
    def add_draw(self, session_id: str, draw_data: Dict[str, Any]) -> bool:
        """Ajoute un tirage à une session"""
        return self.migration_service.add_draw_to_postgres(session_id, draw_data)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """Liste toutes les sessions"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                database='katooling_main_system', 
                user='postgres',
                password='Katulaa_33',
                port=5432
            )
            cursor = conn.cursor()
            
            # Récupérer work_sessions avec tirages
            cursor.execute("""
                SELECT ws.id, ws.name, ws.description, ws.created_at, ws.total_draws,
                       COUNT(sd.id) as actual_draws
                FROM work_sessions ws
                LEFT JOIN session_draws sd ON ws.id = sd.session_id
                GROUP BY ws.id, ws.name, ws.description, ws.created_at, ws.total_draws
                ORDER BY ws.created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': f'work_{row[0]}',
                    'session_name': row[1] or f'Session {row[0]}',
                    'description': row[2] or '',
                    'created_at': row[3].isoformat() if row[3] else None,
                    'total_draws': row[5],  # actual_draws
                    'status': 'active' if row[5] > 0 else 'empty'
                })
            
            cursor.close()
            conn.close()
            return sessions
            
        except Exception as e:
            print(f'Erreur list_sessions: {e}')
            return []
    
    def get_session_draws(self, session_id: str) -> List[Dict[str, Any]]:
        """Récupère les tirages d'une session"""
        session_data = self.get_session(session_id)
        return session_data.get('draws', []) if session_data else []
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Statistiques d'une session"""
        session_data = self.get_session(session_id)
        if not session_data:
            return {}
        
        draws = session_data.get('draws', [])
        lottery_types = {}
        
        for draw in draws:
            lottery_type = draw.get('lottery_type', 'unknown')
            lottery_types[lottery_type] = lottery_types.get(lottery_type, 0) + 1
        
        return {
            'total_draws': len(draws),
            'lottery_types': lottery_types,
            'date_range': {
                'start': draws[0]['date'] if draws else None,
                'end': draws[-1]['date'] if draws else None
            }
        }
    
    def migrate_from_memory(self, unified_session_service) -> Dict[str, bool]:
        """Migre depuis le service mémoire"""
        return self.migration_service.migrate_all_memory_sessions(unified_session_service)