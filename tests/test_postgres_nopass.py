import psycopg2

configs = [
    {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': ''},
    {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'postgres', 'password': 'postgres'},
    {'host': 'localhost', 'database': 'katooling_main_system', 'user': 'katooling', 'password': ''},
]

for i, config in enumerate(configs):
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM katooling_main_system")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"Config {i+1} OK: {count} lignes dans katooling_main_system")
        print(f"Utilisez: {config}")
        break
    except Exception as e:
        print(f"Config {i+1} echouee: {e}")
        
print("Testez manuellement avec vos identifiants PostgreSQL")