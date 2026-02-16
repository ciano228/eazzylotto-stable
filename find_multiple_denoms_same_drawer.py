#!/usr/bin/env python3
"""
Trouver les drawers avec plusieurs dénominations différentes
(même univers, chip, forme mais dénominations différentes)
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

print("=== DRAWERS AVEC DENOMINATIONS MULTIPLES ===\n")

# Trouver les drawers avec plusieurs dénominations
cursor.execute("""
    SELECT 
        univers,
        chip,
        forme,
        drawer,
        array_agg(DISTINCT denomination ORDER BY denomination) as denominations,
        COUNT(DISTINCT denomination) as denom_count
    FROM combinations
    WHERE denomination IS NOT NULL 
    AND denomination != ''
    AND denomination != '---'
    GROUP BY univers, chip, forme, drawer
    HAVING COUNT(DISTINCT denomination) > 1
    ORDER BY univers, CAST(SUBSTRING(chip FROM 5) AS INTEGER), drawer
""")

multiples = cursor.fetchall()

print(f"Total: {len(multiples)} drawers avec dénominations multiples\n")

current_univers = None
for row in multiples:
    if row['univers'] != current_univers:
        current_univers = row['univers']
        print(f"\n{'='*70}")
        print(f"UNIVERS: {current_univers.upper()}")
        print(f"{'='*70}\n")
    
    denoms = row['denominations']
    denom_str = ' / '.join(denoms)
    
    print(f"{row['chip']:8} {row['forme']:20} drawer={row['drawer']:4}")
    print(f"         {row['denom_count']} dénominations: {denom_str}")
    print()

# Stats par univers
print(f"\n{'='*70}")
print("STATISTIQUES PAR UNIVERS")
print(f"{'='*70}\n")

cursor.execute("""
    SELECT 
        univers,
        COUNT(*) as drawers_multiples,
        SUM(denom_count) as total_denoms
    FROM (
        SELECT 
            univers,
            chip,
            forme,
            COUNT(DISTINCT denomination) as denom_count
        FROM combinations
        WHERE denomination IS NOT NULL 
        AND denomination != ''
        AND denomination != '---'
        GROUP BY univers, chip, forme
        HAVING COUNT(DISTINCT denomination) > 1
    ) sub
    GROUP BY univers
    ORDER BY univers
""")

stats = cursor.fetchall()
for stat in stats:
    print(f"{stat['univers']:10} | {stat['drawers_multiples']:3} drawers | {stat['total_denoms']:4} dénominations totales")

conn.close()
print("\n=== FIN ===")
