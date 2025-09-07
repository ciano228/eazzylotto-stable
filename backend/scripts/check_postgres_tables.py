import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Lister toutes les tables
    cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"Tables disponibles: {[t[0] for t in tables]}")
    
    # Si pas de tables, chercher dans d'autres schémas
    if not tables:
        cursor.execute("""
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname != 'information_schema' 
        AND schemaname != 'pg_catalog'
        """)
        all_tables = cursor.fetchall()
        print(f"Toutes les tables: {all_tables}")
    
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}")