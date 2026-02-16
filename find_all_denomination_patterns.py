#!/usr/bin/env python3
"""
Analyser tous les patterns de dénominations
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import re

DB_CONFIG = {
    'host': 'localhost',
    'database': 'katooling_main_system',
    'user': 'postgres',
    'password': 'Katulaa_33',
    'port': 5432
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("=== ANALYSE PATTERNS DENOMINATIONS ===\n")

# Échantillon de dénominations
cursor.execute("""
    SELECT DISTINCT denomination
    FROM combinations
    WHERE denomination IS NOT NULL 
    AND denomination != ''
    AND denomination != '---'
    ORDER BY denomination
    LIMIT 100
""")

denoms = [r['denomination'] for r in cursor.fetchall()]

print("Exemples de dénominations:\n")
for i, d in enumerate(denoms[:30], 1):
    has_slash = '/' in d
    has_dash = '-' in d and not d.startswith('---')
    has_comma = ',' in d
    
    markers = []
    if has_slash: markers.append("SLASH")
    if has_dash: markers.append("DASH")
    if has_comma: markers.append("COMMA")
    
    marker_str = f" [{', '.join(markers)}]" if markers else ""
    print(f"{i:2}. {d:30}{marker_str}")

# Chercher spécifiquement les patterns multiples
print("\n" + "="*60)
print("RECHERCHE PATTERNS MULTIPLES")
print("="*60 + "\n")

patterns = [
    ('%/%', 'SLASH (/)'),
    ('%,%', 'COMMA (,)'),
    ('% / %', 'SLASH avec espaces'),
    ('% , %', 'COMMA avec espaces'),
]

for pattern, name in patterns:
    cursor.execute("""
        SELECT COUNT(DISTINCT denomination) as count
        FROM combinations
        WHERE denomination LIKE %s
    """, (pattern,))
    
    count = cursor.fetchone()['count']
    print(f"{name:25} : {count:4} dénominations")
    
    if count > 0:
        cursor.execute("""
            SELECT DISTINCT univers, chip, forme, denomination
            FROM combinations
            WHERE denomination LIKE %s
            ORDER BY univers, CAST(SUBSTRING(chip FROM 5) AS INTEGER)
            LIMIT 5
        """, (pattern,))
        
        examples = cursor.fetchall()
        print(f"  Exemples:")
        for ex in examples:
            print(f"    {ex['univers']:8} {ex['chip']:8} {ex['forme']:15} : {ex['denomination']}")
        print()

conn.close()
print("=== FIN ===")
