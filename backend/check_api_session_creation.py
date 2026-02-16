#!/usr/bin/env python3
"""
Vérifier quelle table est utilisée par l'API pour créer de nouvelles sessions
"""

import psycopg2
import json

def check_api_session_creation():
    """Vérifier quelle table est utilisée par l'API"""
    
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
        
        print("=== VERIFICATION API SESSION CREATION ===\n")
        
        # 1. Comparer les deux tables
        print("1. COMPARAISON DES TABLES:")
        
        cursor.execute("SELECT COUNT(*) FROM work_sessions")
        work_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        unified_count = cursor.fetchone()[0]
        
        print(f"   - work_sessions: {work_count} sessions")
        print(f"   - unified_sessions: {unified_count} sessions")
        
        # 2. Vérifier les sessions récentes
        print("\n2. SESSIONS RECENTES:")
        
        print("\n   work_sessions (3 plus récentes):")
        cursor.execute("""
            SELECT id, name, created_at, is_active, total_draws
            FROM work_sessions 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        recent_work = cursor.fetchall()
        for session in recent_work:
            print(f"     * ID {session[0]}: {session[1]} (cree: {session[2]}, actif: {session[3]}, tirages: {session[4]})")
        
        print("\n   unified_sessions (3 plus récentes):")
        cursor.execute("""
            SELECT id, name, created_at, is_active, total_draws
            FROM unified_sessions 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        recent_unified = cursor.fetchall()
        for session in recent_unified:
            print(f"     * ID {session[0]}: {session[1]} (cree: {session[2]}, actif: {session[3]}, tirages: {session[4]})")
        
        # 3. Vérifier session_test_001 dans les deux tables
        print("\n3. SESSION_TEST_001 DANS LES DEUX TABLES:")
        
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
        
        if work_test:
            print(f"   - work_sessions: ID {work_test[0]}, cree {work_test[2]}, {work_test[3]} tirages, actif: {work_test[4]}")
            
            # Compter les tirages réels
            cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (work_test[0],))
            work_draws = cursor.fetchone()[0]
            print(f"     Tirages reels dans session_draws: {work_draws}")
        
        if unified_test:
            print(f"   - unified_sessions: ID {unified_test[0]}, cree {unified_test[2]}, {unified_test[3]} tirages, actif: {unified_test[4]}")
            
            # Compter les tirages réels
            cursor.execute("SELECT COUNT(*) FROM unified_draws WHERE session_uuid = (SELECT session_uuid FROM unified_sessions WHERE id = %s)", (unified_test[0],))
            unified_draws = cursor.fetchone()[0]
            print(f"     Tirages reels dans unified_draws: {unified_draws}")
        
        # 4. Vérifier quelle table a plus d'activité récente
        print("\n4. ACTIVITE RECENTE:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM work_sessions 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        recent_work_activity = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM unified_sessions 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        recent_unified_activity = cursor.fetchone()[0]
        
        print(f"   - work_sessions (30 derniers jours): {recent_work_activity} nouvelles sessions")
        print(f"   - unified_sessions (30 derniers jours): {recent_unified_activity} nouvelles sessions")
        
        # 5. Recommandation basée sur l'analyse
        print("\n5. ANALYSE ET RECOMMANDATION:")
        
        if work_test and unified_test:
            work_date = work_test[2]
            unified_date = unified_test[2]
            
            if work_date > unified_date:
                print("   ✅ work_sessions contient la version la plus récente de session_test_001")
                print("   ✅ RECOMMANDATION: Utiliser work_sessions pour les nouvelles sessions")
                recommendation = "work_sessions"
            else:
                print("   ⚠️  unified_sessions contient la version la plus récente de session_test_001")
                print("   ⚠️  RECOMMANDATION: Utiliser unified_sessions pour les nouvelles sessions")
                recommendation = "unified_sessions"
        elif work_test:
            print("   ✅ session_test_001 existe seulement dans work_sessions")
            print("   ✅ RECOMMANDATION: Utiliser work_sessions pour les nouvelles sessions")
            recommendation = "work_sessions"
        elif unified_test:
            print("   ⚠️  session_test_001 existe seulement dans unified_sessions")
            print("   ⚠️  RECOMMANDATION: Utiliser unified_sessions pour les nouvelles sessions")
            recommendation = "unified_sessions"
        else:
            print("   ❌ session_test_001 n'existe dans aucune table")
            recommendation = "work_sessions" if recent_work_activity >= recent_unified_activity else "unified_sessions"
        
        # 6. Vérifier les services utilisés
        print("\n6. SERVICES UTILISES:")
        print("   - KatoolingSessionService lit les DEUX tables")
        print("   - unified_session_service utilise probablement work_sessions")
        print("   - Les interfaces utilisent KatoolingSessionService")
        
        print(f"\n=== CONCLUSION ===")
        print(f"Table recommandée pour nouvelles sessions: {recommendation}")
        print(f"Table de tirages associée: {'session_draws' if recommendation == 'work_sessions' else 'unified_draws'}")
        
        cursor.close()
        conn.close()
        
        return {
            'recommendation': recommendation,
            'work_sessions_count': work_count,
            'unified_sessions_count': unified_count,
            'recent_work_activity': recent_work_activity,
            'recent_unified_activity': recent_unified_activity
        }
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None

if __name__ == "__main__":
    result = check_api_session_creation()
    if result:
        print(f"\nRESULTAT: {result['recommendation']}")