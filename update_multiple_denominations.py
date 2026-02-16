#!/usr/bin/env python3
"""
Mettre à jour les dénominations multiples avec le format "denom1 / denom2"
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

print("=== MISE A JOUR DENOMINATIONS MULTIPLES ===\n")

# Trouver les drawers avec plusieurs dénominations
cursor.execute("""
    SELECT 
        univers,
        chip,
        forme,
        drawer,
        array_agg(DISTINCT denomination ORDER BY denomination) as denominations
    FROM combinations
    WHERE denomination IS NOT NULL 
    AND denomination != ''
    AND denomination != '---'
    GROUP BY univers, chip, forme, drawer
    HAVING COUNT(DISTINCT denomination) > 1
    ORDER BY univers, CAST(SUBSTRING(chip FROM 5) AS INTEGER), drawer
""")

multiples = cursor.fetchall()
total_updated = 0

print(f"Traitement de {len(multiples)} drawers...\n")

for row in multiples:
    univers = row['univers']
    chip = row['chip']
    forme = row['forme']
    drawer = row['drawer']
    denoms = row['denominations']
    
    # Créer la dénomination combinée
    combined_denom = ' / '.join(denoms)
    
    # Mettre à jour toutes les lignes de ce drawer
    cursor.execute("""
        UPDATE combinations
        SET denomination = %s
        WHERE univers = %s 
        AND chip = %s 
        AND forme = %s
        AND drawer = %s
    """, (combined_denom, univers, chip, forme, drawer))
    
    updated = cursor.rowcount
    total_updated += updated
    
    print(f"{univers:10} {chip:8} {forme:20} drawer={drawer:4}")
    print(f"           {combined_denom} ({updated} lignes)")

# Commit
conn.commit()

print(f"\n{'='*70}")
print(f"Total: {total_updated} lignes mises a jour")
print(f"{'='*70}")

# Vérification
cursor.execute("""
    SELECT COUNT(DISTINCT denomination) as count
    FROM combinations
    WHERE denomination LIKE '%/%'
""")

count = cursor.fetchone()['count']
print(f"\nVerification: {count} denominations avec '/' dans la BD")

# Exemple chip44 fruity
cursor.execute("""
    SELECT chip, forme, denomination, drawer
    FROM combinations
    WHERE univers = 'fruity' AND chip = 'chip44' AND forme = 'carre'
    LIMIT 1
""")

example = cursor.fetchone()
if example:
    print(f"\nExemple chip44 fruity carre:")
    print(f"  Denomination: {example['denomination']}")
    print(f"  Drawer: {example['drawer']}")

conn.close()
print("\n=== TERMINE ===")
