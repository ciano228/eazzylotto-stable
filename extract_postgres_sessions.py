#!/usr/bin/env python3
"""
Extraire toutes les sessions existantes de PostgreSQL
"""

import psycopg2
import json
from datetime import datetime

def extract_all_sessions():
    """Extraire toutes les sessions de PostgreSQL"""
    
    # Configuration qui fonctionne
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
        
        print("=== EXTRACTION DES SESSIONS POSTGRESQL ===\n")
        
        # 1. Analyser work_sessions
        print("1. TABLE work_sessions:")
        cursor.execute("SELECT * FROM work_sessions ORDER BY id")
        work_sessions = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'work_sessions' ORDER BY ordinal_position")
        work_columns = [col[0] for col in cursor.fetchall()]
        
        print(f"   Colonnes: {work_columns}")
        print(f"   Total: {len(work_sessions)} sessions")
        
        for session in work_sessions:
            session_dict = dict(zip(work_columns, session))
            print(f"   - ID {session_dict['id']}: {session_dict.get('name', 'Sans nom')}")
            print(f"     Description: {session_dict.get('description', 'N/A')}")
            print(f"     Créé: {session_dict.get('created_at', 'N/A')}")
            print()
        
        # 2. Analyser sessions
        print("2. TABLE sessions:")
        cursor.execute("SELECT * FROM sessions ORDER BY id")
        sessions = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'sessions' ORDER BY ordinal_position")
        sessions_columns = [col[0] for col in cursor.fetchall()]
        
        print(f"   Colonnes: {sessions_columns}")
        print(f"   Total: {len(sessions)} sessions")
        
        for session in sessions:
            session_dict = dict(zip(sessions_columns, session))
            print(f"   - ID {session_dict['id']}: {session_dict.get('name', 'Sans nom')}")
            print(f"     Description: {session_dict.get('description', 'N/A')}")
            print()
        
        # 3. Analyser session_draws
        print("3. TABLE session_draws:")
        cursor.execute("SELECT session_id, COUNT(*) as draw_count FROM session_draws GROUP BY session_id ORDER BY session_id")
        draws_by_session = cursor.fetchall()
        
        print(f"   Total tirages: 218")
        print("   Répartition par session:")
        for session_id, count in draws_by_session:
            print(f"   - Session {session_id}: {count} tirages")
        
        # Détails des tirages pour chaque session
        print("\n   Détails des tirages:")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'session_draws' ORDER BY ordinal_position")
        draws_columns = [col[0] for col in cursor.fetchall()]
        print(f"   Colonnes: {draws_columns}")
        
        for session_id, count in draws_by_session[:3]:  # Limiter aux 3 premières
            cursor.execute("SELECT * FROM session_draws WHERE session_id = %s ORDER BY draw_number LIMIT 3", (session_id,))
            sample_draws = cursor.fetchall()
            
            print(f"\n   Session {session_id} - Exemples de tirages:")
            for draw in sample_draws:
                draw_dict = dict(zip(draws_columns, draw))
                print(f"     Tirage #{draw_dict.get('draw_number', 'N/A')}: {draw_dict}")
        
        # 4. Analyser draws
        print("\n4. TABLE draws:")
        cursor.execute("SELECT * FROM draws ORDER BY id LIMIT 5")
        draws = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'draws' ORDER BY ordinal_position")
        draws_columns = [col[0] for col in cursor.fetchall()]
        
        print(f"   Colonnes: {draws_columns}")
        print(f"   Total: 6 tirages")
        
        for draw in draws:
            draw_dict = dict(zip(draws_columns, draw))
            print(f"   - ID {draw_dict['id']}: {draw_dict}")
        
        # 5. Vérifier les relations
        print("\n5. RELATIONS ENTRE TABLES:")
        
        # Vérifier si work_sessions a des tirages associés
        cursor.execute("""
            SELECT ws.id, ws.name, COUNT(sd.id) as draw_count
            FROM work_sessions ws
            LEFT JOIN session_draws sd ON ws.id = sd.session_id
            GROUP BY ws.id, ws.name
            ORDER BY ws.id
        """)
        
        relations = cursor.fetchall()
        print("   work_sessions -> session_draws:")
        for ws_id, ws_name, draw_count in relations:
            print(f"   - {ws_name} (ID {ws_id}): {draw_count} tirages")
        
        # Vérifier si sessions a des tirages associés
        cursor.execute("""
            SELECT s.id, s.name, COUNT(sd.id) as draw_count
            FROM sessions s
            LEFT JOIN session_draws sd ON s.id = sd.session_id
            GROUP BY s.id, s.name
            ORDER BY s.id
        """)
        
        relations2 = cursor.fetchall()
        print("\n   sessions -> session_draws:")
        for s_id, s_name, draw_count in relations2:
            print(f"   - {s_name} (ID {s_id}): {draw_count} tirages")
        
        cursor.close()
        conn.close()
        
        # 6. Résumé
        print("\n=== RESUME ===")
        print(f"SESSIONS TROUVEES:")
        print(f"- work_sessions: {len(work_sessions)} sessions")
        print(f"- sessions: {len(sessions)} sessions")
        print(f"- session_draws: 218 tirages répartis sur {len(draws_by_session)} sessions")
        print(f"- draws: 6 tirages indépendants")
        
        print(f"\nPOURQUOI INACCESSIBLES:")
        print(f"1. API PostgreSQL cherche dans work_sessions mais avec mauvaise structure")
        print(f"2. Format des données différent de ce qu'attend l'interface")
        print(f"3. Pas de mapping entre les IDs PostgreSQL et les noms de sessions")
        
        print(f"\nSOLUTIONS:")
        print(f"1. Adapter le PostgresSessionService pour lire work_sessions")
        print(f"2. Créer un mapping ID -> nom de session")
        print(f"3. Convertir le format des données pour l'interface")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    extract_all_sessions()