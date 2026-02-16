import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33'
)

cursor = conn.cursor()

# Compter drawers uniques
cursor.execute("""
    SELECT COUNT(DISTINCT drawer_name)
    FROM combinations
    WHERE univers = 'mundo'
    AND drawer_name IS NOT NULL
""")
print("Drawers UNIQUES Mundo:", cursor.fetchone()[0])

# Analyser chip1 avec ordre
print("\n=== CHIP1 - Arrangement Naturel ===")
cursor.execute("""
    SELECT DISTINCT 
        drawer_name,
        forme,
        alpha_ranking,
        denomination
    FROM combinations
    WHERE univers = 'mundo'
    AND chip = 'chip1'
    AND drawer_name IS NOT NULL
    ORDER BY alpha_ranking, drawer_name
""")

for row in cursor.fetchall():
    drawer_name, forme, alpha, denom = row
    print(f"{drawer_name:12} | forme: {forme:10} | alpha: {str(alpha or 'N/A'):3} | denom: {denom or 'N/A'}")

# Analyser chip2
print("\n=== CHIP2 - Arrangement Naturel ===")
cursor.execute("""
    SELECT DISTINCT 
        drawer_name,
        forme,
        alpha_ranking
    FROM combinations
    WHERE univers = 'mundo'
    AND chip = 'chip2'
    AND drawer_name IS NOT NULL
    ORDER BY alpha_ranking, drawer_name
""")

for row in cursor.fetchall():
    drawer_name, forme, alpha = row
    print(f"{drawer_name:12} | forme: {forme:10} | alpha: {str(alpha or 'N/A'):3}")

# Vérifier si alpha_ranking indique l'ordre vertical
print("\n=== ORDRE ALPHA_RANKING (premiers chips) ===")
cursor.execute("""
    SELECT 
        chip,
        drawer_name,
        forme,
        alpha_ranking
    FROM combinations
    WHERE univers = 'mundo'
    AND chip IN ('chip1', 'chip2', 'chip3')
    AND drawer_name IS NOT NULL
    GROUP BY chip, drawer_name, forme, alpha_ranking
    ORDER BY chip, alpha_ranking
    LIMIT 20
""")

current_chip = None
for chip, drawer, forme, alpha in cursor.fetchall():
    if chip != current_chip:
        print(f"\n{chip}:")
        current_chip = chip
    print(f"  alpha={str(alpha or 'N/A'):3} -> {drawer:12} ({forme})")

cursor.close()
conn.close()
