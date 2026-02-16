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

# Vérifier les colonnes de la table
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations'")
columns = [row[0] for row in cursor.fetchall()]
print("Colonnes disponibles:", columns)

# Test avec table 2
cursor.execute("SELECT * FROM combinations WHERE denomination = 'table 2' LIMIT 3")
results = cursor.fetchall()
print(f"Résultats pour 'table 2': {len(results)} lignes")
if results:
    print("Premier résultat:", results[0])

cursor.close()
conn.close()