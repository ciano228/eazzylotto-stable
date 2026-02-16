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
            
            # Vérifier quelle table existe
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name IN ('unified_sessions', 'work_sessions')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f'DEBUG: Tables disponibles: {tables}')
            
            # Standardisation: on utilise work_sessions + session_draws partout.
            table_name = 'work_sessions'
            draws_table = 'session_draws'
            
            print(f'DEBUG: Utilisation de {table_name} et {draws_table}')
            
            cursor.execute(f"""
                SELECT ws.id, ws.name, ws.description, ws.total_draws, 
                       ws.created_at, ws.is_active, ws.numbers_per_draw,
                       ws.number_range_min, ws.number_range_max,
                       ws.lottery_type,
                       (SELECT COUNT(*) FROM {draws_table} sd 
                        WHERE sd.session_id = ws.id AND sd.is_completed = true) as completed_draws
                FROM {table_name} ws
                ORDER BY ws.created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                total = row[3] or 0
                completed = row[10] or 0
                progress = round((completed / total * 100)) if total > 0 else 0
                
                sessions.append({
                    'id': row[0],
                    'session_id': row[0],  # For compatibility
                    'name': row[1],
                    'session_name': row[1],  # For compatibility
                    'description': row[2] or '',
                    'total_draws': total,
                    'created_at': row[4].isoformat() if row[4] else None,
                    'is_active': row[5],
                    'numbers_per_draw': row[6] or 5,
                    'number_range_min': row[7] or 1,
                    'number_range_max': row[8] or 90,
                    'lottery_type': row[9] or 'standard',
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
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une session complète avec ses tirages"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Session
            # Déterminer quelle table utiliser
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name IN ('unified_sessions', 'work_sessions')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Standardisation: on utilise work_sessions + session_draws partout.
            table_name = 'work_sessions'
            draws_table = 'session_draws'
            session_id_col = 'session_id'
            
            cursor.execute(f"""
                SELECT id, name, description, total_draws, 
                       numbers_per_draw, number_range_min, number_range_max,
                       created_at, is_active, current_draw, cycle_length,
                       lottery_schedule, start_date, lottery_type
                FROM {table_name} 
                WHERE id = %s
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # Tirages
            cursor.execute(f"""
                SELECT draw_number, lottery_name, draw_date, winning_numbers,
                       is_completed, cycle_position, is_no_draw, no_draw_reason
                FROM {draws_table} 
                WHERE {session_id_col} = %s 
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
            
            session_data = {
                'id': session_row[0],
                'session_id': session_row[0],  # For compatibility
                'name': session_row[1],
                'session_name': session_row[1],  # For compatibility
                'description': session_row[2] or '',
                'total_draws': session_row[3],
                'numbers_per_draw': session_row[4] or 5,
                'number_range_min': session_row[5] or 1,
                'number_range_max': session_row[6] or 90,
                'created_at': session_row[7].isoformat() if session_row[7] else None,
                'is_active': session_row[8],
                'current_draw': session_row[9] or 1,
                'cycle_length': session_row[10] or 7,
                'lottery_schedule': session_row[11] or [],
                'start_date': session_row[12].isoformat() if session_row[12] else None,
                'lottery_type': session_row[13] or 'standard',
                'draws': draws,
                'completed_draws': len([d for d in draws if d['is_completed']]),
                'progress_percentage': (len([d for d in draws if d['is_completed']]) / max(session_row[3], 1)) * 100
            }
            
            cursor.close()
            conn.close()
            return session_data
            
        except Exception as e:
            print(f'Erreur get_session: {e}')
            return None
    
    def create_session(self, session_data: Dict[str, Any]) -> str:
        """Crée une nouvelle session et ses tirages"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            import uuid
            session_uuid = str(uuid.uuid4())
            
            # Utiliser unified_sessions si elle existe
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'unified_sessions'
            """)
            use_unified = cursor.fetchone() is not None
            
            cursor.execute("""
                INSERT INTO work_sessions (
                    name, description, lottery_type,
                    numbers_per_draw, number_range_min, number_range_max,
                    total_draws, cycle_length, lottery_schedule, start_date, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session_data.get('name', 'Nouvelle Session'),
                session_data.get('description', ''),
                session_data.get('lottery_type', 'standard'),
                session_data.get('numbers_per_draw', 5),
                session_data.get('number_range_min', 1),
                session_data.get('number_range_max', 90),
                session_data.get('total_draws', 0),
                session_data.get('cycle_length', 7),
                json.dumps(session_data.get('lottery_schedule', [])) if session_data.get('lottery_schedule') else None,
                session_data.get('start_date'),
                False
            ))
            
            session_id = cursor.fetchone()[0]
            
            # Créer les tirages
            schedule = session_data.get('schedule', [])
            # Si pas de planning fourni, créer des tirages génériques
            if not schedule and session_data.get('total_draws', 0) > 0:
                for i in range(session_data.get('total_draws')):
                    schedule.append({
                        'draw_number': i + 1,
                        'lottery_name': f"Tirage {i + 1}"
                    })

            for item in schedule:
                cursor.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_name, draw_date,
                        is_completed, cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    item.get('draw_number'),
                    item.get('lottery_name', f"Tirage {item.get('draw_number')}"),
                    item.get('draw_date'),
                    False,
                    item.get('draw_number')
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return session_id
            
        except Exception as e:
            print(f'Erreur create_session: {e}')
            return None
            print(f'Erreur create_session: {e}')
            return None
    
    def add_draw(self, session_uuid: str, draw_data: Dict[str, Any]) -> bool:
        """Ajoute un tirage à une session"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Standardisation: session_uuid est interprété comme session_id (numérique) si possible.
            try:
                session_id = int(session_uuid)
            except Exception:
                raise ValueError(f"session_uuid invalide pour session_draws: {session_uuid}")

            cursor.execute("""
                INSERT INTO session_draws (
                    session_id, draw_number, lottery_name, draw_date,
                    winning_numbers, is_completed, cycle_position
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, draw_number) DO UPDATE SET
                    lottery_name = EXCLUDED.lottery_name,
                    draw_date = EXCLUDED.draw_date,
                    winning_numbers = EXCLUDED.winning_numbers,
                    is_completed = EXCLUDED.is_completed,
                    cycle_position = EXCLUDED.cycle_position,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                session_id,
                draw_data['draw_number'],
                draw_data.get('lottery_name', ''),
                draw_data.get('draw_date'),
                draw_data.get('numbers', []),
                draw_data.get('is_completed', True),
                draw_data.get('cycle_position', 0)
            ))

            # Mettre à jour le compteur (work_sessions)
            cursor.execute("""
                UPDATE work_sessions
                SET total_draws = (
                    SELECT COUNT(*) FROM session_draws
                    WHERE session_id = %s
                ),
                updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (session_id, session_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f'Erreur add_draw: {e}')
            return False
    
    def get_session_draws(self, session_id: int) -> List[Dict[str, Any]]:
        """Récupère uniquement les tirages d'une session"""
        try:
            print(f'\n=== CHARGEMENT TIRAGES ===')
            print(f'Session ID: {session_id}')
            
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Forcer l'utilisation de session_draws
            cursor.execute("""
                SELECT draw_number, lottery_name, draw_date, winning_numbers,
                       is_completed, cycle_position, is_no_draw, no_draw_reason
                FROM session_draws 
                WHERE session_id = %s 
                ORDER BY draw_number
            """, (session_id,))
            
            rows = cursor.fetchall()
            print(f'Lignes trouvées: {len(rows)}')
            
            draws = []
            for i, draw_row in enumerate(rows):
                draw = {
                    'draw_number': draw_row[0],
                    'lottery_name': draw_row[1],
                    'draw_date': draw_row[2].strftime('%Y-%m-%d') if draw_row[2] else None,
                    'winning_numbers': draw_row[3] if draw_row[3] else [],
                    'is_completed': draw_row[4],
                    'cycle_position': draw_row[5],
                    'is_no_draw': draw_row[6] if len(draw_row) > 6 else False,
                    'no_draw_reason': draw_row[7] if len(draw_row) > 7 else None
                }
                draws.append(draw)
                print(f'Tirage {i+1}: {draw}')
            
            cursor.close()
            conn.close()
            
            print('=== CHARGEMENT TERMINÉ ===\n')
            return draws
            
        except Exception as e:
            print(f'Erreur get_session_draws: {e}')
            return []
    
    def get_session_stats(self, session_uuid: str) -> Dict[str, Any]:
        """Statistiques d'une session"""
        try:
            session_id = int(session_uuid)
        except Exception:
            return {}

        session = self.get_session(session_id)
        if not session:
            return {}
        
        draws = session['draws']
        lottery_types = {}
        
        for draw in draws:
            lottery_type = draw.get('lottery_name', 'unknown')
            lottery_types[lottery_type] = lottery_types.get(lottery_type, 0) + 1
        
        return {
            'total_draws': len(draws),
            'completed_draws': session['completed_draws'],
            'progress_percentage': session['progress_percentage'],
            'lottery_types': lottery_types,
            'date_range': {
                'start': draws[0]['date'] if draws else None,
                'end': draws[-1]['date'] if draws else None
            }
        }

    def activate_session(self, session_id: int) -> bool:
        """Active une session et désactive les autres"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Déterminer quelle table utiliser
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name IN ('unified_sessions', 'work_sessions')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            table_name = 'unified_sessions' if 'unified_sessions' in tables else 'work_sessions'
            
            # Désactiver toutes les sessions
            cursor.execute(f"UPDATE {table_name} SET is_active = false")
            
            # Activer la session demandée
            cursor.execute(f"UPDATE {table_name} SET is_active = true WHERE id = %s", (session_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f'Erreur activate_session: {e}')
            return False

    def update_draw_results(self, session_id: int, draw_number: int, winning_numbers: List[int]) -> bool:
        """Met à jour les résultats d'un tirage existant"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE session_draws 
                SET winning_numbers = %s, 
                    is_completed = true,
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s AND draw_number = %s
            """, (winning_numbers, session_id, draw_number))
            
            row_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return row_count > 0
            
        except Exception as e:
            print(f'Erreur update_draw_results: {e}')
            return False
    
    def delete_draw(self, session_id: int, draw_number: int) -> bool:
        """Supprime un tirage d'une session"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM session_draws 
                WHERE session_id = %s AND draw_number = %s
            """, (session_id, draw_number))
            
            row_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return row_count > 0
            
        except Exception as e:
            print(f'Erreur delete_draw: {e}')
            return False
    
    def save_draw_result(self, session_id: int, draw_number: int, draw_data: Dict[str, Any]) -> bool:
        """Sauvegarde ou met à jour un résultat de tirage"""
        try:
            print(f'\n=== SAUVEGARDE TIRAGE ===')
            print(f'Session ID: {session_id}')
            print(f'Draw Number: {draw_number}')
            print(f'Data: {draw_data}')
            
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Forcer l'utilisation de session_draws pour simplifier
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_draws (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    draw_number INTEGER NOT NULL,
                    lottery_name VARCHAR(255),
                    draw_date DATE,
                    winning_numbers INTEGER[],
                    is_completed BOOLEAN DEFAULT FALSE,
                    is_no_draw BOOLEAN DEFAULT FALSE,
                    no_draw_reason TEXT,
                    cycle_position INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, draw_number)
                )
            """)
            
            winning_numbers = draw_data.get('numbers', [])
            is_completed = len(winning_numbers) > 0 and not draw_data.get('is_no_draw', False)
            
            print(f'Winning numbers: {winning_numbers}')
            print(f'Is completed: {is_completed}')
            
            # Utiliser UPDATE direct avec les vraies valeurs
            cursor.execute("""
                UPDATE session_draws 
                SET lottery_name = %s,
                    draw_date = %s,
                    winning_numbers = %s,
                    is_completed = %s,
                    is_no_draw = %s,
                    no_draw_reason = %s,
                    updated_at = CURRENT_TIMESTAMP
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
            
            rows_updated = cursor.rowcount
            print(f'Lignes mises à jour: {rows_updated}')
            
            # Si aucune ligne mise à jour, insérer
            if rows_updated == 0:
                cursor.execute("""
                    INSERT INTO session_draws (
                        session_id, draw_number, lottery_name, draw_date,
                        winning_numbers, is_completed, is_no_draw, no_draw_reason,
                        cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id,
                    draw_number,
                    draw_data.get('lottery_name', ''),
                    draw_data.get('draw_date'),
                    winning_numbers,
                    is_completed,
                    draw_data.get('is_no_draw', False),
                    draw_data.get('no_draw_reason'),
                    draw_number
                ))
                print(f'Nouveau tirage inséré')
            
            conn.commit()
            
            # Vérification immédiate
            cursor.execute("""
                SELECT winning_numbers, is_completed, lottery_name 
                FROM session_draws 
                WHERE session_id = %s AND draw_number = %s
            """, (session_id, draw_number))
            
            result = cursor.fetchone()
            print(f'Vérification: {result}')
            
            cursor.close()
            conn.close()
            
            print('=== SAUVEGARDE TERMINÉE ===\n')
            return True
            
        except Exception as e:
            print(f'ERREUR save_draw_result: {e}')
            import traceback
            traceback.print_exc()
            return False