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
    
    # Test table mundo
    cursor.execute("SELECT COUNT(*) FROM mundo")
    count = cursor.fetchone()[0]
    print(f"Mundo: {count} lignes")
    
    # Test formes mundo
    cursor.execute("""
    SELECT DISTINCT forme, COUNT(*) as freq 
    FROM mundo 
    WHERE forme IS NOT NULL 
    GROUP BY forme ORDER BY freq DESC LIMIT 5
    """)
    formes = cursor.fetchall()
    print(f"Mundo formes: {formes}")
    
    # Test chip 1 mundo
    cursor.execute("""
    SELECT forme, denomination, COUNT(*) as freq
    FROM mundo 
    WHERE chip = '1' AND forme IS NOT NULL
    GROUP BY forme, denomination LIMIT 5
    """)
    chip1 = cursor.fetchall()
    print(f"Mundo chip 1: {chip1}")
    
    conn.close()
    print("Structure PostgreSQL OK!")
    
except Exception as e:
    print(f"Erreur: {e}")