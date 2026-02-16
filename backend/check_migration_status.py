#!/usr/bin/env python3
"""
Vérifier si les migrations sont déjà réalisées
"""

import psycopg2

def check_migration_status():
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
        
        print("=== VERIFICATION STATUT MIGRATION ===\n")
        
        # 1. Comparer les comptes
        cursor.execute("SELECT COUNT(*) FROM work_sessions")
        work_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        unified_count = cursor.fetchone()[0]
        
        print(f"work_sessions: {work_count} sessions")
        print(f"unified_sessions: {unified_count} sessions")
        
        # 2. Vérifier si toutes les sessions work_sessions sont dans unified_sessions
        cursor.execute("""
            SELECT w.name
            FROM work_sessions w
            LEFT JOIN unified_sessions u ON w.name = u.name
            WHERE u.name IS NULL
        """)
        missing_sessions = cursor.fetchall()
        
        if missing_sessions:
            print(f"\nSessions manquantes dans unified_sessions: {len(missing_sessions)}")
            for session in missing_sessions:
                print(f"  - {session[0]}")
        else:
            print("\nToutes les sessions work_sessions sont dans unified_sessions ✓")
        
        # 3. Comparer les tirages
        cursor.execute("SELECT COUNT(*) FROM session_draws")
        session_draws_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_draws")
        unified_draws_count = cursor.fetchone()[0]
        
        print(f"\nsession_draws: {session_draws_count} tirages")
        print(f"unified_draws: {unified_draws_count} tirages")
        
        # 4. Vérifier les sessions supplémentaires dans unified
        cursor.execute("""
            SELECT u.name
            FROM unified_sessions u
            LEFT JOIN work_sessions w ON u.name = w.name
            WHERE w.name IS NULL
        """)
        extra_sessions = cursor.fetchall()
        
        if extra_sessions:
            print(f"\nSessions supplémentaires dans unified_sessions: {len(extra_sessions)}")
            for session in extra_sessions:
                print(f"  - {session[0]}")
        
        # 5. Conclusion
        print(f"\n=== CONCLUSION ===")
        if unified_count >= work_count and not missing_sessions:
            print("✓ MIGRATION DEJA REALISEE")
            print("✓ unified_sessions contient toutes les sessions")
            print("✓ Pas besoin de migration supplémentaire")
            
            if unified_count > work_count:
                print(f"✓ unified_sessions a même {unified_count - work_count} sessions supplémentaires")
            
            return "COMPLETE"
        else:
            print("⚠ MIGRATION INCOMPLETE")
            print("⚠ Certaines sessions manquent dans unified_sessions")
            return "INCOMPLETE"
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")
        return "ERROR"

if __name__ == "__main__":
    status = check_migration_status()
    print(f"\nSTATUT: {status}")