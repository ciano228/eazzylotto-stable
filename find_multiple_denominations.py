#!/usr/bin/env python3
"""
Trouver les drawers avec dénominations multiples (séparées par /)
"""
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("=== DENOMINATIONS MULTIPLES (avec /) ===\n")

# Trouver toutes les dénominations avec /
cursor.execute("""
    SELECT univers, chip, forme, denomination, drawer
    FROM (
        SELECT DISTINCT univers, chip, forme, denomination, drawer
        FROM combinations
        WHERE denomination LIKE '%/%'
    ) sub
    ORDER BY univers, CAST(SUBSTRING(chip FROM 5) AS INTEGER), drawer
    LIMIT 50
""")

rows = cursor.fetchall()

print(f"Total trouvé: {len(rows)} drawers avec dénominations multiples\n")

current_univers = None
for row in rows:
    if row['univers'] != current_univers:
        current_univers = row['univers']
        print(f"\n{'='*60}")
        print(f"UNIVERS: {current_univers.upper()}")
        print(f"{'='*60}\n")
    
    denoms = row['denomination'].split('/')
    print(f"{row['chip']:8} {row['forme']:20} drawer={row['drawer']:4}")
    print(f"         Dénominations: {' / '.join(denoms)}")
    print()

# Compter par univers
print(f"\n{'='*60}")
print("STATISTIQUES PAR UNIVERS")
print(f"{'='*60}\n")

cursor.execute("""
    SELECT 
        univers,
        COUNT(DISTINCT drawer) as drawers_multiples,
        COUNT(*) as total_lignes
    FROM combinations
    WHERE denomination LIKE '%/%'
    GROUP BY univers
    ORDER BY univers
""")

stats = cursor.fetchall()
for stat in stats:
    print(f"{stat['univers']:10} | {stat['drawers_multiples']:3} drawers | {stat['total_lignes']:4} lignes")

conn.close()
print("\n=== FIN ===")
