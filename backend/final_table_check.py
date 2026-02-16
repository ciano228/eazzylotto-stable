#!/usr/bin/env python3
"""
Verification finale de la table utilisee pour creer des sessions
"""

import psycopg2
from datetime import datetime

def final_table_check():
    """Verification finale"""
    
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
        
        print("=== VERIFICATION FINALE ===\n")
        
        # Verifier session_test_001 dans les deux tables
        cursor.execute("""
            SELECT id, name, created_at, total_draws, is_active
            FROM work_sessions 
            WHERE name = 'session_test_001'
        """)
        work_test = cursor.fetchone()
        
        cursor.execute("""
            SELECT id, name, created_at, total_draws, is_active
            FROM unified_sessions 
            WHERE name = 'session_test_001'
        """)
        unified_test = cursor.fetchone()
        
        print("SESSION_TEST_001:")
        if work_test:
            print(f"  work_sessions: ID {work_test[0]}, cree {work_test[2]}, {work_test[3]} tirages")
            
            # Compter tirages reels
            cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (work_test[0],))
            work_draws = cursor.fetchone()[0]
            print(f"    Tirages reels: {work_draws}")
        
        if unified_test:
            print(f"  unified_sessions: ID {unified_test[0]}, cree {unified_test[2]}, {unified_test[3]} tirages")
            
            # Compter tirages reels
            cursor.execute("SELECT COUNT(*) FROM unified_draws WHERE session_uuid = (SELECT session_uuid FROM unified_sessions WHERE id = %s)", (unified_test[0],))
            unified_draws = cursor.fetchone()[0]
            print(f"    Tirages reels: {unified_draws}")
        
        # Activite recente
        cursor.execute("""
            SELECT COUNT(*) FROM work_sessions 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        recent_work = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM unified_sessions 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        recent_unified = cursor.fetchone()[0]
        
        print(f"\nACTIVITE RECENTE (30 jours):")
        print(f"  work_sessions: {recent_work} nouvelles sessions")
        print(f"  unified_sessions: {recent_unified} nouvelles sessions")
        
        # Conclusion
        print(f"\nCONCLUSION:")
        
        if work_test and unified_test:
            work_date = work_test[2]
            unified_date = unified_test[2]
            
            if work_date > unified_date:
                print("  work_sessions contient la version la plus recente")
                print("  RECOMMANDATION: Utiliser work_sessions")
                recommendation = "work_sessions"
            else:
                print("  unified_sessions contient la version la plus recente")
                print("  RECOMMANDATION: Utiliser unified_sessions")
                recommendation = "unified_sessions"
        elif recent_work > recent_unified:
            print("  work_sessions a plus d'activite recente")
            print("  RECOMMANDATION: Utiliser work_sessions")
            recommendation = "work_sessions"
        else:
            print("  unified_sessions semble plus utilise")
            print("  RECOMMANDATION: Utiliser unified_sessions")
            recommendation = "unified_sessions"
        
        print(f"\nTABLE RECOMMANDEE: {recommendation}")
        print(f"TABLE TIRAGES: {'session_draws' if recommendation == 'work_sessions' else 'unified_draws'}")
        
        cursor.close()
        conn.close()
        
        return recommendation
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None

if __name__ == "__main__":
    result = final_table_check()
    print(f"\nRESULTAT FINAL: {result}")