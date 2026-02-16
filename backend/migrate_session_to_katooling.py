#!/usr/bin/env python3
"""
Migrer session_test_001 vers katooling_main_system
"""

import psycopg2
from unified_session_service import unified_session_service
import json

def migrate_session_to_katooling():
    """Migre session_test_001 vers katooling_main_system"""
    
    # Configuration BD katooling
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33'
    }
    
    try:
        # Récupérer session_test_001 depuis le service unifié
        session_data = unified_session_service.get_session_for_smart_input('session_test_001')
        
        print(f"Migration session: {session_data['session_name']}")
        print(f"Tirages: {len(session_data['draws'])}")
        
        # Connexion à katooling_main_system
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Insérer dans unified_sessions
        cursor.execute("""
            INSERT INTO unified_sessions (
                session_uuid, name, description, session_type, lottery_type,
                numbers_per_draw, number_range_min, number_range_max, total_draws
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_uuid) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                total_draws = EXCLUDED.total_draws
        """, (
            session_data['session_name'],
            session_data['session_name'],
            'Session de test avec 42 tirages sur 6 périodes',
            'test_session',
            'Loto Test',
            session_data['metadata']['numbers_per_draw'],
            session_data['metadata']['number_range_min'],
            session_data['metadata']['number_range_max'],
            session_data['total_draws']
        ))
        
        print("Session inseree dans unified_sessions")
        
        # 2. Insérer les tirages dans unified_draws
        cursor.execute("DELETE FROM unified_draws WHERE session_uuid = %s", (session_data['session_name'],))
        
        for draw in session_data['draws']:
            metadata = {
                'period': draw['period'],
                'day_of_week': draw['day_of_week'],
                'is_period_end': draw.get('is_period_end', False),
                'universe': session_data['metadata']['universe']
            }
            
            cursor.execute("""
                INSERT INTO unified_draws (
                    session_uuid, draw_number, lottery_name, draw_date,
                    winning_numbers, is_completed, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                session_data['session_name'],
                draw['draw_number'],
                draw['loto_name'],
                draw['draw_date'],
                json.dumps(draw['numbers']) if draw['numbers'] else '[]',
                draw['is_completed'],
                json.dumps(metadata)
            ))
        
        print(f"{len(session_data['draws'])} tirages inseres dans unified_draws")
        
        # 3. Vérification
        cursor.execute("SELECT COUNT(*) FROM unified_draws WHERE session_uuid = %s", (session_data['session_name'],))
        count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Migration terminee: {count} tirages dans katooling_main_system")
        return True
        
    except Exception as e:
        print(f"Erreur migration: {e}")
        return False

def test_katooling_access():
    """Teste l'accès à session_test_001 dans katooling_main_system"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33'
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Vérifier la session
        cursor.execute("""
            SELECT name, total_draws, session_type
            FROM unified_sessions 
            WHERE session_uuid = 'session_test_001'
        """)
        session = cursor.fetchone()
        
        if session:
            print(f"Session trouvee: {session[0]} ({session[1]} tirages)")
            
            # Vérifier les tirages
            cursor.execute("""
                SELECT COUNT(*), 
                       COUNT(CASE WHEN is_completed THEN 1 END) as completed
                FROM unified_draws 
                WHERE session_uuid = 'session_test_001'
            """)
            draws_info = cursor.fetchone()
            
            print(f"Tirages: {draws_info[1]}/{draws_info[0]} completes")
            
            # Exemple de tirages
            cursor.execute("""
                SELECT draw_number, lottery_name, draw_date, winning_numbers
                FROM unified_draws 
                WHERE session_uuid = 'session_test_001'
                ORDER BY draw_number
                LIMIT 5
            """)
            examples = cursor.fetchall()
            
            print("Exemples de tirages:")
            for draw in examples:
                numbers = json.loads(draw[3]) if draw[3] else []
                print(f"  #{draw[0]} {draw[1]} ({draw[2]}): {numbers}")
        else:
            print("Session non trouvee dans katooling_main_system")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur test: {e}")

if __name__ == "__main__":
    print("Migration session_test_001 vers katooling_main_system...")
    
    success = migrate_session_to_katooling()
    
    if success:
        print("\nTest d'acces...")
        test_katooling_access()
        
        print("\nsession_test_001 est maintenant disponible dans katooling_main_system")
        print("Accessible via les routes /api/katooling/*")
    else:
        print("\nMigration echouee")