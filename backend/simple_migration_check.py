#!/usr/bin/env python3
"""
Verification simple du statut de migration
"""

import psycopg2

def simple_migration_check():
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
        
        print("=== VERIFICATION MIGRATION ===\n")
        
        # Comptes
        cursor.execute("SELECT COUNT(*) FROM work_sessions")
        work_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        unified_count = cursor.fetchone()[0]
        
        print(f"work_sessions: {work_count} sessions")
        print(f"unified_sessions: {unified_count} sessions")
        
        # Sessions manquantes
        cursor.execute("""
            SELECT COUNT(*)
            FROM work_sessions w
            LEFT JOIN unified_sessions u ON w.name = u.name
            WHERE u.name IS NULL
        """)
        missing_count = cursor.fetchone()[0]
        
        print(f"Sessions manquantes dans unified: {missing_count}")
        
        # Tirages
        cursor.execute("SELECT COUNT(*) FROM session_draws")
        session_draws_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_draws")
        unified_draws_count = cursor.fetchone()[0]
        
        print(f"session_draws: {session_draws_count} tirages")
        print(f"unified_draws: {unified_draws_count} tirages")
        
        # Conclusion
        print(f"\nCONCLUSION:")
        if unified_count >= work_count and missing_count == 0:
            print("MIGRATION DEJA REALISEE")
            print("unified_sessions contient toutes les sessions")
            print("Pas besoin de migration supplementaire")
            
            if unified_count > work_count:
                extra = unified_count - work_count
                print(f"unified_sessions a meme {extra} sessions supplementaires")
            
            return True
        else:
            print("MIGRATION INCOMPLETE")
            print("Certaines sessions manquent")
            return False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    complete = simple_migration_check()
    print(f"\nMIGRATION COMPLETE: {complete}")