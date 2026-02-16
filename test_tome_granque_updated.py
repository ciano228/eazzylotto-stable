import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'host': os.getenv('KATULA_DB_HOST', 'localhost'),
    'database': os.getenv('KATULA_DB_NAME', 'katooling_main_system'),
    'user': os.getenv('KATULA_DB_USER', 'postgres'),
    'password': os.getenv('KATULA_DB_PASSWORD', 'Katulaa_33'),
    'port': int(os.getenv('KATULA_DB_PORT', '5432'))
}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

print("=== VERIFICATION TOMES 1-10 ET GRANQUES ===")

# Tomes distincts
cursor.execute("SELECT tome, COUNT(*) FROM combinations WHERE univers = 'mundo' GROUP BY tome ORDER BY tome")
tomes = cursor.fetchall()
print(f"Tomes trouvés: {tomes}")

# Granques distincts  
cursor.execute("SELECT granque_name, COUNT(*) FROM combinations WHERE univers = 'mundo' GROUP BY granque_name ORDER BY granque_name")
granques = cursor.fetchall()
print(f"Granques trouvés: {granques}")

cursor.close()
conn.close()