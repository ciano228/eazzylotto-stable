#!/usr/bin/env python3
"""
Vérifier quelle table est utilisée pour créer de nouvelles sessions
"""

import psycopg2
import json

def check_session_creation_tables():
    """Vérifier les tables utilisées pour créer des sessions"""
    
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
        
        print("=== VÉRIFICATION DES TABLES DE SESSIONS ===\n")
        
        # 1. Vérifier work_sessions
        print("1. TABLE work_sessions:")
        cursor.execute("SELECT COUNT(*) FROM work_sessions")
        work_count = cursor.fetchone()[0]
        print(f"   - Nombre de sessions: {work_count}")
        
        if work_count > 0:
            cursor.execute("""
                SELECT id, name, created_at, is_active 
                FROM work_sessions 
                ORDER BY id DESC 
                LIMIT 3
            """)
            recent_work = cursor.fetchall()
            print("   - Sessions récentes:")
            for session in recent_work:
                print(f"     * ID {session[0]}: {session[1]} (créé: {session[2]}, actif: {session[3]})")
        
        # 2. Vérifier unified_sessions
        print("\n2. TABLE unified_sessions:")
        cursor.execute("SELECT COUNT(*) FROM unified_sessions")
        unified_count = cursor.fetchone()[0]
        print(f"   - Nombre de sessions: {unified_count}")
        
        if unified_count > 0:
            cursor.execute("""
                SELECT id, name, created_at, session_type 
                FROM unified_sessions 
                ORDER BY id DESC 
                LIMIT 3
            """)
            recent_unified = cursor.fetchall()
            print("   - Sessions récentes:")
            for session in recent_unified:
                print(f"     * ID {session[0]}: {session[1]} (créé: {session[2]}, type: {session[3]})")
        
        # 3. Vérifier les champs requis pour créer une session
        print("\n3. CHAMPS REQUIS POUR CRÉATION:")
        
        print("\n   work_sessions:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'work_sessions'
            ORDER BY ordinal_position
        """)
        work_columns = cursor.fetchall()
        for col in work_columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"     - {col[0]}: {col[1]} {nullable}{default}")
        
        print("\n   unified_sessions:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'unified_sessions'
            ORDER BY ordinal_position
        """)
        unified_columns = cursor.fetchall()
        for col in unified_columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"     - {col[0]}: {col[1]} {nullable}{default}")
        
        # 4. Vérifier les tables de tirages associées
        print("\n4. TABLES DE TIRAGES:")
        
        cursor.execute("SELECT COUNT(*) FROM session_draws")
        session_draws_count = cursor.fetchone()[0]
        print(f"   - session_draws: {session_draws_count} tirages")
        
        cursor.execute("SELECT COUNT(*) FROM unified_draws")
        unified_draws_count = cursor.fetchone()[0]
        print(f"   - unified_draws: {unified_draws_count} tirages")
        
        # 5. Vérifier la session_test_001 récemment créée
        print("\n5. SESSION_TEST_001:")
        
        cursor.execute("SELECT id, name FROM work_sessions WHERE name = 'session_test_001'")
        work_test = cursor.fetchone()
        if work_test:
            print(f"   - Trouvée dans work_sessions: ID {work_test[0]}")
            
            # Compter ses tirages
            cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (work_test[0],))
            test_draws = cursor.fetchone()[0]
            print(f"   - Nombre de tirages: {test_draws}")
        else:
            print("   - Non trouvée dans work_sessions")
        
        cursor.execute("SELECT id, name FROM unified_sessions WHERE name = 'session_test_001'")
        unified_test = cursor.fetchone()
        if unified_test:
            print(f"   - Trouvée dans unified_sessions: ID {unified_test[0]}")
        else:
            print("   - Non trouvée dans unified_sessions")
        
        # 6. Recommandation
        print("\n6. RECOMMANDATION:")
        if work_count > unified_count:
            print("   ✅ work_sessions semble être la table principale")
            print("   ✅ Les nouvelles sessions devraient être créées dans work_sessions")
            print("   ✅ Les tirages associés vont dans session_draws")
        else:
            print("   ⚠️  unified_sessions pourrait être la table principale")
            print("   ⚠️  Vérifier l'usage réel dans l'application")
        
        cursor.close()
        conn.close()
        
        return {
            'work_sessions_count': work_count,
            'unified_sessions_count': unified_count,
            'session_draws_count': session_draws_count,
            'unified_draws_count': unified_draws_count,
            'recommendation': 'work_sessions' if work_count > unified_count else 'unified_sessions'
        }
        
    except Exception as e:
        print(f"Erreur: {e}")
        return None

if __name__ == "__main__":
    result = check_session_creation_tables()
    if result:
        print(f"\n=== RÉSUMÉ ===")
        print(f"Table recommandée pour nouvelles sessions: {result['recommendation']}")