"""
Recipe Generator for Synthetic Attributes
Convertit les patterns découverts en recettes structurées
"""

import json
import os

def generate_recipes(report_path, output_path):
    if not os.path.exists(report_path):
        print(f"Erreur: Le rapport {report_path} n'existe pas.")
        return

    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    discovered_patterns = report.get('top_patterns', [])
    recipes = []
    seen_component_sets = set()

    for pattern_data in discovered_patterns:
        pattern_str = pattern_data['pattern']
        # Exemple pattern: "forme:rectangle_tome:tome1"
        
        parts = pattern_str.split('_')
        components = []
        
        for part in parts:
            if ':' in part:
                attr, value = part.split(':', 1)
                components.append(attr)
            else:
                components.append(part)

        # Normaliser et trier les composants pour la déduplication
        comp_set = tuple(sorted(list(set(components))))
        
        if comp_set in seen_component_sets:
            continue
            
        seen_component_sets.add(comp_set)
        
        # Créer un nom générique pour le type moléculaire
        recipe_name = "_".join(comp_set)
        formula = "_".join([f"{{{c}}}" for c in comp_set])

        recipe = {
            "name": recipe_name,
            "type": "concatenation",
            "components": list(comp_set),
            "formula": formula,
            "discovered_frequency": pattern_data['frequency_percent'], # Fréquence du pattern déclencheur
            "num_attributes": len(comp_set),
            "category": pattern_data.get('category', 'other'),
            "description": f"Type moléculaire basé sur {recipe_name}"
        }
        
        recipes.append(recipe)

    # Sauvegarder les recettes
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)

    print(f"Génération terminée: {len(recipes)} recettes créées dans {output_path}")

if __name__ == "__main__":
    REPORT_FILE = 'pattern_discovery_report_session25.json'
    OUTPUT_FILE = 'synthetic_recipes.json'
    generate_recipes(REPORT_FILE, OUTPUT_FILE)
