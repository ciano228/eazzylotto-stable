#!/usr/bin/env python3
"""
Créer une table unifiée pour toutes les sessions
"""

import psycopg2
from datetime import datetime

def create_unified_sessions_table():
    """Créer la table unifiée et migrer toutes les sessions"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("=== CRÉATION TABLE UNIFIÉE ===\n")
        
        # 1. Créer la nouvelle table unifiée
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_sessions (
                id SERIAL PRIMARY KEY,
                session_uuid VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                session_type VARCHAR(50) DEFAULT 'lottery',
                lottery_type VARCHAR(100),
                numbers_per_draw INTEGER DEFAULT 5,
                number_range_min INTEGER DEFAULT 1,
                number_range_max INTEGER DEFAULT 90,
                total_draws INTEGER DEFAULT 0,
                current_draw INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_table VARCHAR(50),
                source_id INTEGER,
                metadata JSONB
            )
        """)
        
        # 2. Créer la table unifiée des tirages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_draws (
                id SERIAL PRIMARY KEY,
                session_uuid VARCHAR(100) REFERENCES unified_sessions(session_uuid),
                draw_number INTEGER NOT NULL,
                lottery_name VARCHAR(255),
                draw_date DATE,
                winning_numbers INTEGER[],
                is_completed BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cycle_position INTEGER DEFAULT 0,
                metadata JSONB,
                UNIQUE(session_uuid, draw_number)
            )
        """)
        
        print("✅ Tables créées")
        
        # 3. Migrer work_sessions
        cursor.execute("SELECT * FROM work_sessions ORDER BY id")
        work_sessions = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'work_sessions' ORDER BY ordinal_position")
        work_columns = [col[0] for col in cursor.fetchall()]
        
        print(f"📊 Migration work_sessions: {len(work_sessions)} sessions")
        
        for session in work_sessions:
            session_dict = dict(zip(work_columns, session))
            session_uuid = f"work_{session_dict['id']}"
            
            cursor.execute("""
                INSERT INTO unified_sessions (
                    session_uuid, name, description, session_type, lottery_type,
                    numbers_per_draw, number_range_min, number_range_max,
                    total_draws, current_draw, is_active, created_at,
                    source_table, source_id, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_uuid) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                session_uuid,
                session_dict.get('name') or f"Session {session_dict['id']}",
                session_dict.get('description'),
                'lottery',
                session_dict.get('lottery_type'),
                session_dict.get('numbers_per_draw', 5),
                session_dict.get('number_range_min', 1),
                session_dict.get('number_range_max', 90),
                session_dict.get('total_draws', 0),
                session_dict.get('current_draw', 1),
                session_dict.get('is_active', True),
                session_dict.get('created_at', datetime.now()),
                'work_sessions',
                session_dict['id'],
                {}
            ))
            
            # Migrer les tirages associés
            cursor.execute("SELECT * FROM session_draws WHERE session_id = %s ORDER BY draw_number", (session_dict['id'],))
            draws = cursor.fetchall()
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'session_draws' ORDER BY ordinal_position")
            draw_columns = [col[0] for col in cursor.fetchall()]
            
            for draw in draws:
                draw_dict = dict(zip(draw_columns, draw))
                
                cursor.execute("""
                    INSERT INTO unified_draws (
                        session_uuid, draw_number, lottery_name, draw_date,
                        winning_numbers, is_completed, created_at, cycle_position
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_uuid, draw_number) DO UPDATE SET
                        lottery_name = EXCLUDED.lottery_name,
                        winning_numbers = EXCLUDED.winning_numbers
                """, (
                    session_uuid,
                    draw_dict['draw_number'],
                    draw_dict.get('lottery_name'),
                    draw_dict.get('draw_date'),
                    draw_dict.get('winning_numbers', []),
                    draw_dict.get('is_completed', True),
                    draw_dict.get('created_at', datetime.now()),
                    draw_dict.get('cycle_position', 0)
                ))
        
        # 4. Migrer sessions
        cursor.execute("SELECT * FROM sessions ORDER BY id")
        sessions = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'sessions' ORDER BY ordinal_position")
        sessions_columns = [col[0] for col in cursor.fetchall()]
        
        print(f"📊 Migration sessions: {len(sessions)} sessions")
        
        for session in sessions:
            session_dict = dict(zip(sessions_columns, session))
            session_uuid = f"session_{session_dict['id']}"
            
            cursor.execute("""
                INSERT INTO unified_sessions (
                    session_uuid, name, description, session_type, lottery_type,
                    numbers_per_draw, number_range_min, number_range_max,
                    total_draws, current_draw, is_active, created_at,
                    source_table, source_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_uuid) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                session_uuid,
                session_dict.get('name') or f"Session {session_dict['id']}",
                session_dict.get('description'),
                'lottery',
                session_dict.get('lottery_type'),
                session_dict.get('numbers_per_draw', 5),
                session_dict.get('number_range_min', 1),
                session_dict.get('number_range_max', 90),
                session_dict.get('total_draws', 0),
                session_dict.get('current_draw', 1),
                session_dict.get('is_active', True),
                session_dict.get('created_at', datetime.now()),
                'sessions',
                session_dict['id']
            ))
        
        # 5. Mettre à jour les compteurs
        cursor.execute("""
            UPDATE unified_sessions 
            SET total_draws = (
                SELECT COUNT(*) 
                FROM unified_draws 
                WHERE unified_draws.session_uuid = unified_sessions.session_uuid
            )
        """)
        
        conn.commit()
        
        # 6. Vérification
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_draws")
        total_draws = cursor.fetchone()[0]
        
        print(f"✅ Migration terminée:")
        print(f"   - {total_sessions} sessions unifiées")
        print(f"   - {total_draws} tirages unifiés")
        
        # 7. Afficher le résumé
        cursor.execute("""
            SELECT session_uuid, name, total_draws, source_table
            FROM unified_sessions 
            ORDER BY total_draws DESC
        """)
        
        print(f"\n📋 Sessions unifiées:")
        for row in cursor.fetchall():
            print(f"   - {row[1]} ({row[0]}): {row[2]} tirages [source: {row[3]}]")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    create_unified_sessions_table()