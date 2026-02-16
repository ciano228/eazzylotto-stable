#!/usr/bin/env python3
"""
Correctif pour le mapping des sessions PostgreSQL
Résout l'erreur 'pg_work_6' en créant un mapping correct
"""

import psycopg2
import json

def fix_session_mapping():
    """Corrige le mapping des sessions PostgreSQL"""
    
    # Essayer les différentes configurations de connexion
    db_configs = [
        {'host': 'localhost', 'database': 'katula_db', 'user': 'postgres', 'password': 'Katula2024'},
        {'host': 'localhost', 'database': 'katula_db', 'user': 'postgres', 'password': 'Katulaa_33'},
        {'host': 'localhost', 'database': 'postgres', 'user': 'postgres', 'password': 'Katula2024'},
        {'host': 'localhost', 'database': 'postgres', 'user': 'postgres', 'password': 'Katulaa_33'}
    ]
    
    conn = None
    for config in db_configs:
        try:
            conn = psycopg2.connect(**config)
            print(f"Connexion réussie avec {config}")
            break
        except Exception as e:
            print(f"Echec avec {config}: {e}")
            continue
    
    if not conn:
        print("Impossible de se connecter à PostgreSQL")
        return create_fallback_mapping()
    
    cursor = conn.cursor()
    
    try:
        # Vérifier les tables disponibles
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"\nTables disponibles: {[t[0] for t in tables]}")
        
        # Chercher les sessions dans work_sessions
        if ('work_sessions',) in tables:
            cursor.execute("SELECT id, name FROM work_sessions ORDER BY id")
            work_sessions = cursor.fetchall()
            print(f"\nSessions work_sessions:")
            for session_id, name in work_sessions:
                print(f"  ID: {session_id}, Nom: {name}")
                
                # Vérifier les tirages pour cette session
                cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
                draw_count = cursor.fetchone()[0]
                print(f"    Tirages: {draw_count}")
        
        # Chercher dans sessions
        if ('sessions',) in tables:
            cursor.execute("SELECT id, name FROM sessions ORDER BY id")
            sessions = cursor.fetchall()
            print(f"\nSessions table:")
            for session_id, name in sessions:
                print(f"  ID: {session_id}, Nom: {name}")
        
        # Chercher dans unified_sessions
        if ('unified_sessions',) in tables:
            cursor.execute("SELECT session_id, session_name FROM unified_sessions ORDER BY session_id")
            unified_sessions = cursor.fetchall()
            print(f"\nSessions unifiees:")
            for session_id, name in unified_sessions:
                print(f"  ID: {session_id}, Nom: {name}")
        
        # Créer le mapping correct
        session_mapping = create_session_mapping(cursor, tables)
        
        cursor.close()
        conn.close()
        
        return session_mapping
        
    except Exception as e:
        print(f"Erreur lors de la verification: {e}")
        cursor.close()
        conn.close()
        return create_fallback_mapping()

def create_session_mapping(cursor, tables):
    """Crée un mapping correct des sessions"""
    mapping = {}
    
    try:
        # Mapper work_sessions
        if ('work_sessions',) in tables:
            cursor.execute("SELECT id, name FROM work_sessions")
            for session_id, name in cursor.fetchall():
                mapping[f"pg_work_{session_id}"] = {
                    'real_id': session_id,
                    'name': name,
                    'table': 'work_sessions',
                    'type': 'postgresql'
                }
        
        # Mapper sessions
        if ('sessions',) in tables:
            cursor.execute("SELECT id, name FROM sessions")
            for session_id, name in cursor.fetchall():
                mapping[f"pg_session_{session_id}"] = {
                    'real_id': session_id,
                    'name': name,
                    'table': 'sessions',
                    'type': 'postgresql'
                }
        
        # Mapper unified_sessions
        if ('unified_sessions',) in tables:
            cursor.execute("SELECT session_id, session_name FROM unified_sessions")
            for session_id, name in cursor.fetchall():
                mapping[session_id] = {
                    'real_id': session_id,
                    'name': name,
                    'table': 'unified_sessions',
                    'type': 'unified'
                }
        
        print(f"\nMapping cree: {len(mapping)} sessions mappees")
        for key, value in mapping.items():
            print(f"  {key} -> {value['name']} ({value['table']})")
        
        return mapping
        
    except Exception as e:
        print(f"Erreur creation mapping: {e}")
        return {}

def create_fallback_mapping():
    """Cree un mapping de fallback si PostgreSQL n'est pas accessible"""
    print("\nCreation mapping de fallback...")
    
    # Sessions de test par defaut
    fallback_mapping = {
        'session_test_001': {
            'real_id': 'session_test_001',
            'name': 'Session Test 001',
            'table': 'memory',
            'type': 'memory'
        },
        'algeria': {
            'real_id': 'algeria',
            'name': 'Algeria Session',
            'table': 'memory',
            'type': 'memory'
        },
        'casablanca': {
            'real_id': 'casablanca',
            'name': 'Casablanca Games',
            'table': 'memory',
            'type': 'memory'
        }
    }
    
    print(f"Mapping fallback cree: {len(fallback_mapping)} sessions")
    return fallback_mapping

def save_mapping_to_file(mapping):
    """Sauvegarde le mapping dans un fichier JSON"""
    try:
        with open('session_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        print(f"Mapping sauvegarde dans session_mapping.json")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")

if __name__ == "__main__":
    print("Correction du mapping des sessions PostgreSQL...")
    mapping = fix_session_mapping()
    
    if mapping:
        save_mapping_to_file(mapping)
        
        # Afficher les sessions disponibles pour l'interface
        print(f"\nSessions disponibles pour l'interface:")
        for session_key, session_info in mapping.items():
            print(f"  - {session_key}: {session_info['name']}")
        
        # Vérifier spécifiquement 'algeria'
        algeria_sessions = [k for k, v in mapping.items() if 'algeria' in v['name'].lower()]
        if algeria_sessions:
            print(f"\nSessions Algeria trouvées:")
            for session in algeria_sessions:
                print(f"  - Utiliser: {session}")
        else:
            print(f"\nAucune session Algeria trouvée dans le mapping")
    else:
        print("Aucun mapping créé")