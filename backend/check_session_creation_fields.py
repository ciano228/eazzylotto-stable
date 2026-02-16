#!/usr/bin/env python3
"""
Vérifier les champs nécessaires pour créer une session loto dans katooling_main_system
"""

import psycopg2

def check_session_creation_fields():
    """Vérifier les colonnes des tables de sessions et tirages"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33'
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("=== COLONNES POUR CREATION SESSION ===")
        
        # Vérifier work_sessions (table principale des sessions)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'work_sessions'
            ORDER BY ordinal_position
        """)
        
        work_sessions_cols = cursor.fetchall()
        print("\nwork_sessions (création session):")
        for col in work_sessions_cols:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  {col[0]} ({col[1]}) {nullable}")
        
        # Vérifier session_draws (table des tirages)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'session_draws'
            ORDER BY ordinal_position
        """)
        
        session_draws_cols = cursor.fetchall()
        print("\nsession_draws (enregistrement tirages):")
        for col in session_draws_cols:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  {col[0]} ({col[1]}) {nullable}")
        
        cursor.close()
        conn.close()
        
        return work_sessions_cols, session_draws_cols
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None, None

if __name__ == "__main__":
    check_session_creation_fields()