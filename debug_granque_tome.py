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

print("=== DIAGNOSTIC GRANQUES ET TOMES ===")

# Vérifier les colonnes
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'combinations' AND column_name IN ('granque_name', 'tome')")
columns = [row[0] for row in cursor.fetchall()]
print(f"Colonnes trouvées: {columns}")

# Échantillon de données
cursor.execute("SELECT chip, forme, denomination, petique, tome, granque_name FROM combinations WHERE univers = 'mundo' LIMIT 10")
results = cursor.fetchall()
print(f"\nÉchantillon de données (10 premières lignes):")
for row in results:
    print(f"  {row}")

# Compter les valeurs NULL
cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo' AND granque_name IS NULL")
null_granques = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo' AND tome IS NULL")
null_tomes = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM combinations WHERE univers = 'mundo'")
total = cursor.fetchone()[0]

print(f"\nStatistiques NULL pour mundo:")
print(f"  Total combinations: {total}")
print(f"  Granques NULL: {null_granques}")
print(f"  Tomes NULL: {null_tomes}")

# Valeurs distinctes
cursor.execute("SELECT DISTINCT granque_name FROM combinations WHERE univers = 'mundo' AND granque_name IS NOT NULL")
granques = [row[0] for row in cursor.fetchall()]
print(f"\nGranques distinctes: {granques}")

cursor.execute("SELECT DISTINCT tome FROM combinations WHERE univers = 'mundo' AND tome IS NOT NULL")
tomes = [row[0] for row in cursor.fetchall()]
print(f"Tomes distinctes: {tomes}")

cursor.close()
conn.close()