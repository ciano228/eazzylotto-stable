#!/usr/bin/env python3
"""
Vérifier la structure de katooling_main_system avant migration
"""

import psycopg2

def check_katooling_structure():
    """Vérifier la structure des tables unified_sessions et unified_draws"""
    
    db_config = {
        'host': 'localhost',
        'database': 'katooling_main_system',
        'user': 'postgres',
        'password': 'Katulaa_33'
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Vérifier unified_sessions
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'unified_sessions'
            ORDER BY ordinal_position
        """)
        
        sessions_columns = cursor.fetchall()
        print("Structure unified_sessions:")
        for col in sessions_columns:
            print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        # Vérifier unified_draws
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'unified_draws'
            ORDER BY ordinal_position
        """)
        
        draws_columns = cursor.fetchall()
        print("\nStructure unified_draws:")
        for col in draws_columns:
            print(f"  {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    check_katooling_structure()