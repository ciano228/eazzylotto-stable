import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33'
)

cursor = conn.cursor()

print("=" * 80)
print("VÉRIFICATION DRAWERS MUNDO")
print("=" * 80)

# 1. Compter les drawers UNIQUES
cursor.execute("""
    SELECT COUNT(DISTINCT drawer_name)
    FROM combinations
    WHERE univers = 'mundo'
    AND drawer_name IS NOT NULL
""")
unique_drawers = cursor.fetchone()[0]
print(f"\nDrawers UNIQUES dans Mundo: {unique_drawers}")

# 2. Compter toutes les entrées
cursor.execute("""
    SELECT COUNT(*)
    FROM combinations
    WHERE univers = 'mundo'
    AND drawer_name IS NOT NULL
""")
total_entries = cursor.fetchone()[0]
print(f"Total d'entrees avec drawer_name: {total_entries}")

# 3. Analyser l'arrangement pour les premiers chips
print("\n" + "=" * 80)
print("ARRANGEMENT NATUREL DES DRAWERS (Premiers chips)")
print("=" * 80)

for chip_num in [1, 2, 3, 10, 15]:
    chip = f"chip{chip_num}"
    
    cursor.execute("""
        SELECT DISTINCT 
            drawer_name,
            forme,
            denomination,
            alpha_ranking,
            drawer
        FROM combinations
        WHERE univers = 'mundo'
        AND chip = %s
        AND drawer_name IS NOT NULL
        ORDER BY drawer_name
    """, (chip,))
    
    drawers = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"CHIP {chip_num}: {len(drawers)} drawers")
    print(f"{'='*60}")
    
    for drawer_name, forme, denomination, alpha_ranking, drawer_id in drawers:
        print(f"  {drawer_name:12} | forme: {forme:10} | denom: {denomination or 'N/A':20} | alpha: {alpha_ranking or 'N/A':3} | drawer: {drawer_id}")

# 4. Vérifier s'il y a un ordre alpha_ranking
print("\n" + "=" * 80)
print("ANALYSE DE L'ORDRE (alpha_ranking)")
print("=" * 80)

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
    ORDER BY chip, alpha_ranking, drawer_name
""")

results = cursor.fetchall()
current_chip = None
for chip, drawer_name, forme, alpha_ranking in results:
    if chip != current_chip:
        print(f"\n{chip}:")
        current_chip = chip
    print(f"  alpha={alpha_ranking or 'N/A':3} → {drawer_name:12} ({forme})")

# 5. Vérifier l'empilement vertical (par forme?)
print("\n" + "=" * 80)
print("DRAWERS PAR FORME DANS CHIP1 (Empilement vertical?)")
print("=" * 80)

cursor.execute("""
    SELECT DISTINCT 
        forme,
        drawer_name,
        alpha_ranking
    FROM combinations
    WHERE univers = 'mundo'
    AND chip = 'chip1'
    AND drawer_name IS NOT NULL
    ORDER BY forme, drawer_name
""")

results = cursor.fetchall()
current_forme = None
for forme, drawer_name, alpha_ranking in results:
    if forme != current_forme:
        print(f"\n{forme.upper()}:")
        current_forme = forme
    print(f"  {drawer_name} (alpha: {alpha_ranking or 'N/A'})")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("ANALYSE TERMINÉE")
print("=" * 80)
