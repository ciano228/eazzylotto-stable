import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33'
)

cursor = conn.cursor()

# Structure de la table drawers
print("=== Structure table drawers ===")
cursor.execute("SELECT * FROM drawers LIMIT 10")
cols = [desc[0] for desc in cursor.description]
print(f"Colonnes: {cols}\n")

for row in cursor.fetchall():
    print(dict(zip(cols, row)))

# Drawer avec référence chip
print("\n=== Drawers avec chip_reference (combinations) ===")
cursor.execute("""
    SELECT DISTINCT drawer_name, chip, forme, univers 
    FROM combinations 
    WHERE drawer_name IS NOT NULL 
    ORDER BY drawer_name 
    LIMIT 20
""")

for row in cursor.fetchall():
    drawer_name, chip, forme, univers = row
    print(f"{drawer_name} -> chip={chip}, forme={forme}, univers={univers}")

cursor.close()
conn.close()
