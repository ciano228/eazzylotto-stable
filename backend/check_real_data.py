"""
Script pour vérifier les vraies données de la combinaison 34-38 depuis PostgreSQL
"""
import psycopg2

# Connexion à PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33',
    port=5432
)

cursor = conn.cursor()

# Récupérer les colonnes
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='combinations' 
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cursor.fetchall()]

print("=" * 80)
print("COLONNES DE LA TABLE combinations")
print("=" * 80)
for i, col in enumerate(columns, 1):
    print(f"{i:3}. {col}")

print("\n" + "=" * 80)
print("DONNEES REELLES POUR LA COMBINAISON 34-38")
print("=" * 80)

# Récupérer les données de 34-38
cursor.execute("SELECT * FROM combinations WHERE num1=34 AND num2=38")
row = cursor.fetchone()

if row:
    print("\n[OK] COMBINAISON TROUVEE !\n")
    for i, col in enumerate(columns):
        if row[i] is not None:
            print(f"{col:25} : {row[i]}")
else:
    print("\n[ERREUR] COMBINAISON 34-38 NON TROUVEE DANS LA BASE DE DONNEES\n")

conn.close()

print("\n" + "=" * 80)
