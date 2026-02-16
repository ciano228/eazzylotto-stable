import psycopg2
import json
from collections import defaultdict

conn = psycopg2.connect(
    host='localhost',
    database='katooling_main_system',
    user='postgres',
    password='Katulaa_33'
)

cursor = conn.cursor()

# Récupérer la structure drawer par chip pour mundo
query = """
    SELECT DISTINCT 
        chip,
        drawer_name,
        drawer,
        forme,
        denomination,
        alpha_ranking
    FROM combinations
    WHERE univers = 'mundo'
    AND drawer_name IS NOT NULL
    ORDER BY chip, drawer_name
"""

cursor.execute(query)
rows = cursor.fetchall()

# Organiser par chip
chip_structure = defaultdict(list)

for row in rows:
    chip, drawer_name, drawer, forme, denomination, alpha_ranking = row
    
    chip_structure[chip].append({
        "drawer_name": drawer_name,
        "drawer": drawer,
        "forme": forme,
        "denomination": denomination,
        "alpha_ranking": alpha_ranking
    })

print("=== Structure Drawers par Chip (MUNDO) ===\n")

# Afficher les 5 premiers chips
for i, (chip, drawers) in enumerate(list(chip_structure.items())[:5]):
    print(f"\n{chip}: ({len(drawers)} drawers)")
    for drawer in drawers[:10]:  # Max 10 drawers affichés
        print(f"  - {drawer['drawer_name']}: {drawer['forme']} (denom: {drawer['denomination'] or 'N/A'})")
    if len(drawers) > 10:
        print(f"  ... et {len(drawers) - 10} autres drawers")

print(f"\n\nTotal chips: {len(chip_structure)}")
print(f"Total drawers: {sum(len(drawers) for drawers in chip_structure.values())}")

# Sauvegarder
result = {
    "universe": "mundo",
    "chip_structure": {k: v for k, v in chip_structure.items()},
    "statistics": {
        "total_chips": len(chip_structure),
        "total_drawers": sum(len(drawers) for drawers in chip_structure.values())
    }
}

with open('chip_structure_mundo.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("\nStructure sauvegardee dans chip_structure_mundo.json")

cursor.close()
conn.close()
