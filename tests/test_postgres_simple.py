import psycopg2

# Configuration PostgreSQL
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
    
    # Test univers
    cursor.execute("SELECT DISTINCT univers FROM katooling_main_system LIMIT 5")
    univers = cursor.fetchall()
    print(f"Univers: {[u[0] for u in univers]}")
    
    # Test formes Mundo
    cursor.execute("""
    SELECT DISTINCT forme, COUNT(*) as freq 
    FROM katooling_main_system 
    WHERE univers = 'mundo' AND forme IS NOT NULL 
    GROUP BY forme ORDER BY freq DESC LIMIT 5
    """)
    formes = cursor.fetchall()
    print(f"Mundo formes: {formes}")
    
    conn.close()
    print("PostgreSQL OK!")
    
except Exception as e:
    print(f"Erreur: {e}")
    print("Modifiez le mot de passe dans DB_CONFIG")