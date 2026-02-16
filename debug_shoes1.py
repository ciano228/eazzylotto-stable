#!/usr/bin/env python3
"""
Debug: Vérifier shoes 1 dans chip1 mundo
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

print("=== DEBUG SHOES 1 CHIP1 MUNDO ===\n")

# Toutes les lignes chip1 mundo
cursor.execute("""
    SELECT chip, forme, denomination, drawer
    FROM combinations
    WHERE univers = 'mundo' AND chip = 'chip1'
    ORDER BY 
        CASE forme
            WHEN 'carre' THEN 1
            WHEN 'triangle' THEN 2
            WHEN 'rectangle' THEN 3
            WHEN 'cercle' THEN 4
        END,
        denomination
""")

rows = cursor.fetchall()

print("Toutes les lignes chip1 mundo (ordre: carre, triangle, rectangle, cercle):\n")
for i, row in enumerate(rows, 1):
    marker = " <-- SHOES 1" if row['denomination'] == 'shoes 1' else ""
    print(f"{i:2}. forme={row['forme']:10} | denom={row['denomination']:20} | drawer={row['drawer']}{marker}")

print("\n" + "="*60)
print("ANALYSE:")
print("="*60)

# Compter les formes distinctes
cursor.execute("""
    SELECT forme, COUNT(*) as count
    FROM combinations
    WHERE univers = 'mundo' AND chip = 'chip1'
    AND denomination IS NOT NULL AND denomination != '' AND denomination != '---'
    GROUP BY forme
    ORDER BY 
        CASE forme
            WHEN 'carre' THEN 1
            WHEN 'triangle' THEN 2
            WHEN 'rectangle' THEN 3
            WHEN 'cercle' THEN 4
        END
""")

formes = cursor.fetchall()
print("\nFormes peuplees dans chip1:")
for i, f in enumerate(formes, 1):
    print(f"  Drawer {i}: {f['forme']:10} ({f['count']} lignes)")

# Vérifier shoes 1
cursor.execute("""
    SELECT forme, drawer
    FROM combinations
    WHERE univers = 'mundo' AND chip = 'chip1' AND denomination = 'shoes 1'
""")

shoes = cursor.fetchone()
if shoes:
    print(f"\nshoes 1 est dans forme={shoes['forme']} -> drawer={shoes['drawer']}")
    print(f"\nVotre attente: drawer 3 (si shoes 1 = 3eme forme)")
    print(f"Resultat actuel: drawer {shoes['drawer']}")
    
    if shoes['forme'] == 'cercle':
        print("\n[EXPLICATION] shoes 1 est dans forme='cercle'")
        print("Si chip1 a: carre(drawer1), triangle(drawer2), rectangle(drawer3), cercle(drawer4)")
        print("Alors shoes 1 (cercle) = drawer 4 est CORRECT")
        print("\nMais si vous attendiez drawer 3, cela signifie:")
        print("  - Soit 'rectangle' n'existe pas dans chip1")
        print("  - Soit shoes 1 devrait etre dans 'rectangle' et non 'cercle'")

conn.close()
