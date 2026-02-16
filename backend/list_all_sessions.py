#!/usr/bin/env python3
"""
Lister toutes les sessions dans les deux tables
"""

import psycopg2

def list_all_sessions():
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
        
        print("=== TOUTES LES SESSIONS ===\n")
        
        # work_sessions
        print("TABLE work_sessions:")
        cursor.execute("""
            SELECT id, name, created_at, total_draws, is_active
            FROM work_sessions 
            ORDER BY id
        """)
        work_sessions = cursor.fetchall()
        
        for session in work_sessions:
            print(f"  ID {session[0]}: {session[1]} ({session[3]} tirages, actif: {session[4]})")
        
        print(f"\nTotal work_sessions: {len(work_sessions)}")
        
        # unified_sessions
        print("\nTABLE unified_sessions:")
        cursor.execute("""
            SELECT id, name, created_at, total_draws, is_active
            FROM unified_sessions 
            ORDER BY id
        """)
        unified_sessions = cursor.fetchall()
        
        for session in unified_sessions:
            print(f"  ID {session[0]}: {session[1]} ({session[3]} tirages, actif: {session[4]})")
        
        print(f"\nTotal unified_sessions: {len(unified_sessions)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    list_all_sessions()