import requests
import json

# Tester le nouvel endpoint
url = "http://localhost:8001/api/analytics/chip-drawers-structure?universe=mundo"

try:
    response = requests.get(url)
    data = response.json()
    
    print("=== Structure Drawers par Chip ===\n")
    print(f"Univers: {data['universe']}")
    print(f"Stats: {data['statistics']}\n")
    
    # Afficher les 5 premiers chips
    chip_structure = data['chip_structure']
    for i, (chip, drawers) in enumerate(list(chip_structure.items())[:5]):
        print(f"\n{chip}:")
        for drawer in drawers:
            print(f"  - {drawer['drawer_name']}: {drawer['forme']} ({drawer['denomination'] or 'N/A'})")
    
    print(f"\n... et {len(chip_structure) - 5} autres chips")
    
    # Sauvegarder la structure complète
    with open('chip_structure_mundo.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Structure sauvegardée dans chip_structure_mundo.json")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
