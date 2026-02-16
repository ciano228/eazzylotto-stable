#!/usr/bin/env python3
import psycopg2

# Test différentes configurations PostgreSQL
configs = [
    {'db': 'postgres', 'user': 'postgres', 'pass': 'admin123'},
    {'db': 'postgres', 'user': 'postgres', 'pass': 'postgres'},
    {'db': 'postgres', 'user': 'postgres', 'pass': ''},
    {'db': 'katula_db', 'user': 'postgres', 'pass': 'admin123'},
    {'db': 'katula_db', 'user': 'postgres', 'pass': 'postgres'},
    {'db': 'katooling_main_system', 'user': 'postgres', 'pass': 'Katula2024'},
    {'db': 'katooling_main_system', 'user': 'postgres', 'pass': 'admin123'},
]

for config in configs:
    try:
        conn = psycopg2.connect(
            host='localhost',
            database=config['db'],
            user=config['user'],
            password=config['pass'],
            port=5432
        )
        cursor = conn.cursor()
        
        print(f"SUCCESS: {config['db']} avec {config['user']}:{config['pass']}")
        
        # Lister les bases de données
        if config['db'] == 'postgres':
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [db[0] for db in cursor.fetchall()]
            print(f"  Bases disponibles: {databases}")
        
        # Lister les tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [t[0] for t in cursor.fetchall()]
        print(f"  Tables ({len(tables)}): {tables[:5]}{'...' if len(tables) > 5 else ''}")
        
        # Chercher tables de sessions/tirages
        session_tables = [t for t in tables if any(k in t.lower() for k in ['session', 'work', 'projet'])]
        draw_tables = [t for t in tables if any(k in t.lower() for k in ['draw', 'tirage', 'resultat', 'loto', 'lottery'])]
        
        if session_tables:
            print(f"  SESSIONS: {session_tables}")
        if draw_tables:
            print(f"  TIRAGES: {draw_tables}")
        
        cursor.close()
        conn.close()
        print()
        
    except Exception as e:
        print(f"FAILED: {config['db']} avec {config['user']}:{config['pass']} - {e}")