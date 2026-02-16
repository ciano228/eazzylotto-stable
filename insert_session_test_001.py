#!/usr/bin/env python3
"""
Insérer session_test_001 dans la table unifiée
"""

import psycopg2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def insert_session_test_001():
    """Insérer session_test_001 avec tous ses paramètres"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33',
        'port': 5432
    }
    
    try:
        # Récupérer session_test_001 depuis le service unifié
        from backend.unified_session_service import unified_session_service
        
        session_data = unified_session_service.initialize_session_test_001()
        
        print("=== INSERTION SESSION_TEST_001 ===")
        print(f"Session: {session_data['session_name']}")
        print(f"Tirages: {len(session_data['draws'])}")
        print(f"Périodes: {session_data['periods']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Insérer la session
        session_uuid = "session_test_001"
        
        cursor.execute("""
            INSERT INTO unified_sessions (
                session_uuid, name, description, session_type, lottery_type,
                numbers_per_draw, number_range_min, number_range_max,
                total_draws, current_draw, is_active, created_at,
                source_table, source_id, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (session_uuid) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                total_draws = EXCLUDED.total_draws,
                metadata = EXCLUDED.metadata,
                updated_at = CURRENT_TIMESTAMP
        """, (
            session_uuid,
            session_data['session_name'],
            'Session de test complète avec 6 périodes de 7 tirages (mardi à lundi)',
            'lottery',
            'test_katula',
            session_data['metadata']['numbers_per_draw'],
            session_data['metadata']['number_range_min'],
            session_data['metadata']['number_range_max'],
            session_data['total_draws'],
            session_data['current_draw'],
            True,
            session_data['created_at'],
            'unified_session_service',
            0,
            '{"cycle_type": "weekly", "period_duration": 7, "periods": 6, "universe": "mundo"}'
        ))
        
        print(f"Session inseree: {session_uuid}")
        
        # 2. Insérer tous les tirages
        for draw in session_data['draws']:
            cursor.execute("""
                INSERT INTO unified_draws (
                    session_uuid, draw_number, lottery_name, draw_date,
                    winning_numbers, is_completed, created_at, cycle_position, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (session_uuid, draw_number) DO UPDATE SET
                    lottery_name = EXCLUDED.lottery_name,
                    draw_date = EXCLUDED.draw_date,
                    winning_numbers = EXCLUDED.winning_numbers,
                    is_completed = EXCLUDED.is_completed,
                    metadata = EXCLUDED.metadata
            """, (
                session_uuid,
                draw['draw_number'],
                draw['loto_name'],
                draw['draw_date'],
                draw['numbers'],
                draw['is_completed'],
                draw['draw_date'],
                draw['day_of_week'],
                f'{{"period": {draw["period"]}, "day_of_week": {draw["day_of_week"]}, "is_period_end": {str(draw.get("is_period_end", False)).lower()}}}'
            ))
        
        print(f"Tirages inseres: {len(session_data['draws'])}")
        
        # 3. Mettre à jour le compteur
        cursor.execute("""
            UPDATE unified_sessions 
            SET total_draws = (
                SELECT COUNT(*) FROM unified_draws 
                WHERE session_uuid = %s
            ),
            updated_at = CURRENT_TIMESTAMP
            WHERE session_uuid = %s
        """, (session_uuid, session_uuid))
        
        conn.commit()
        
        # 4. Vérification
        cursor.execute("""
            SELECT us.session_uuid, us.name, us.total_draws, COUNT(ud.id) as actual_draws
            FROM unified_sessions us
            LEFT JOIN unified_draws ud ON us.session_uuid = ud.session_uuid
            WHERE us.session_uuid = %s
            GROUP BY us.session_uuid, us.name, us.total_draws
        """, (session_uuid,))
        
        result = cursor.fetchone()
        print(f"Verification: {result[1]} - {result[2]} tirages declares, {result[3]} tirages reels")
        
        # 5. Afficher quelques exemples de tirages
        cursor.execute("""
            SELECT draw_number, lottery_name, draw_date, winning_numbers, metadata
            FROM unified_draws 
            WHERE session_uuid = %s 
            ORDER BY draw_number 
            LIMIT 5
        """, (session_uuid,))
        
        print("Exemples de tirages:")
        for row in cursor.fetchall():
            metadata = row[4] if row[4] else {}
            period = metadata.get('period', '?')
            is_end = metadata.get('is_period_end', False)
            end_marker = " [FIN PERIODE]" if is_end else ""
            print(f"  #{row[0]} - {row[1]} ({row[2]}) - P{period}: {row[3]}{end_marker}")
        
        cursor.close()
        conn.close()
        
        print("SUCCESS: session_test_001 inseree dans la table unifiee")
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    insert_session_test_001()