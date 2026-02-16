import psycopg2
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json

class MigrationService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'database': 'katooling_main_system',
            'user': 'postgres',
            'password': 'Katulaa_33',
            'port': 5432
        }
    
    def migrate_session_to_postgres(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Migre une session du cache mémoire vers PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insérer dans work_sessions
            cursor.execute("""
                INSERT INTO work_sessions (session_id, session_name, created_at, status, total_draws)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO UPDATE SET
                    session_name = EXCLUDED.session_name,
                    status = EXCLUDED.status,
                    total_draws = EXCLUDED.total_draws
            """, (
                session_id,
                session_data.get('name', session_id),
                datetime.now(),
                'active',
                len(session_data.get('draws', []))
            ))
            
            # Insérer les tirages dans session_draws
            for draw in session_data.get('draws', []):
                cursor.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_type, draw_date, 
                        numbers, combinations, analysis_data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id, draw_number) DO UPDATE SET
                        lottery_type = EXCLUDED.lottery_type,
                        draw_date = EXCLUDED.draw_date,
                        numbers = EXCLUDED.numbers,
                        combinations = EXCLUDED.combinations,
                        analysis_data = EXCLUDED.analysis_data
                """, (
                    session_id,
                    draw['draw_number'],
                    draw['lottery_type'],
                    datetime.strptime(draw['date'], '%Y-%m-%d').date(),
                    json.dumps(draw['numbers']),
                    json.dumps(draw.get('combinations', [])),
                    json.dumps(draw.get('analysis', {}))
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur migration: {e}")
            return False
    
    def load_session_from_postgres(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Charge une session depuis PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Récupérer la session
            cursor.execute("""
                SELECT session_name, created_at, status, total_draws
                FROM work_sessions WHERE session_id = %s
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # Récupérer les tirages
            cursor.execute("""
                SELECT draw_number, lottery_type, draw_date, numbers, combinations, analysis_data
                FROM session_draws 
                WHERE session_id = %s 
                ORDER BY draw_number
            """, (session_id,))
            
            draws_rows = cursor.fetchall()
            
            # Construire la structure de session
            session_data = {
                'name': session_row[0],
                'created_at': session_row[1].isoformat() if session_row[1] else None,
                'status': session_row[2],
                'total_draws': session_row[3],
                'draws': []
            }
            
            for draw_row in draws_rows:
                draw_data = {
                    'draw_number': draw_row[0],
                    'lottery_type': draw_row[1],
                    'date': draw_row[2].strftime('%Y-%m-%d') if draw_row[2] else None,
                    'numbers': json.loads(draw_row[3]) if draw_row[3] else [],
                    'combinations': json.loads(draw_row[4]) if draw_row[4] else [],
                    'analysis': json.loads(draw_row[5]) if draw_row[5] else {}
                }
                session_data['draws'].append(draw_data)
            
            cursor.close()
            conn.close()
            return session_data
            
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return None
    
    def list_postgres_sessions(self) -> List[Dict[str, Any]]:
        """Liste toutes les sessions PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, session_name, created_at, status, total_draws
                FROM work_sessions 
                ORDER BY created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'name': row[1],
                    'created_at': row[2].isoformat() if row[2] else None,
                    'status': row[3],
                    'total_draws': row[4]
                })
            
            cursor.close()
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Erreur liste sessions: {e}")
            return []
    
    def migrate_all_memory_sessions(self, unified_session_service) -> Dict[str, bool]:
        """Migre toutes les sessions du cache mémoire vers PostgreSQL"""
        results = {}
        
        # Récupérer toutes les sessions du cache
        for session_id, session_data in unified_session_service.sessions_cache.items():
            success = self.migrate_session_to_postgres(session_id, session_data)
            results[session_id] = success
        
        return results
    
    def add_draw_to_postgres(self, session_id: str, draw_data: Dict[str, Any]) -> bool:
        """Ajoute un tirage directement à PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insérer le tirage
            cursor.execute("""
                INSERT INTO session_draws (
                    session_id, draw_number, lottery_type, draw_date, 
                    numbers, combinations, analysis_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, draw_number) DO UPDATE SET
                    lottery_type = EXCLUDED.lottery_type,
                    draw_date = EXCLUDED.draw_date,
                    numbers = EXCLUDED.numbers,
                    combinations = EXCLUDED.combinations,
                    analysis_data = EXCLUDED.analysis_data
            """, (
                session_id,
                draw_data['draw_number'],
                draw_data['lottery_type'],
                datetime.strptime(draw_data['date'], '%Y-%m-%d').date(),
                json.dumps(draw_data['numbers']),
                json.dumps(draw_data.get('combinations', [])),
                json.dumps(draw_data.get('analysis', {}))
            ))
            
            # Mettre à jour le compteur de tirages
            cursor.execute("""
                UPDATE work_sessions 
                SET total_draws = (
                    SELECT COUNT(*) FROM session_draws WHERE session_id = %s
                )
                WHERE session_id = %s
            """, (session_id, session_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur ajout tirage: {e}")
            return False
    
    def create_session_in_postgres(self, session_id: str, session_name: str) -> bool:
        """Crée une nouvelle session dans PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO work_sessions (session_id, session_name, created_at, status, total_draws)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_id) DO NOTHING
            """, (session_id, session_name, datetime.now(), 'active', 0))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur création session: {e}")
            return False