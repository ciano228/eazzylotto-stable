#!/usr/bin/env python3
"""
Test de l'API avec dénominations multiples simulées
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Simuler une réponse API avec dénominations multiples
def simulate_api_response():
    # Données simulées comme si elles venaient de la BD
    simulated_data = {
        "status": "success",
        "formes_data": {
            "carre": [{
                "denomination": "river 6/bed 1",
                "frequency": 1,
                "multiple": True
            }],
            "triangle": [{
                "denomination": "forest 3/mountain 2/lake 1",
                "frequency": 1,
                "multiple": True
            }],
            "cercle": [{
                "denomination": "star 9",
                "frequency": 1,
                "multiple": False
            }]
        },
        "total_items": 3,
        "source": "database"
    }
    
    print("=== SIMULATION DENOMINATIONS MULTIPLES ===")
    print(f"Données simulées: {simulated_data}")
    
    # Traitement comme dans le frontend
    elements = []
    for forme, denominations in simulated_data["formes_data"].items():
        for denom_data in denominations:
            elements.append({
                "type": "real_data",
                "forme": forme,
                "denomination": denom_data["denomination"],
                "frequency": denom_data["frequency"],
                "multiple": denom_data.get("multiple", False)
            })
    
    print(f"\nÉléments traités:")
    for element in elements:
        print(f"  {element['forme']}: {element['denomination']} (multiple: {element['multiple']})")
        
        # Simulation de l'affichage frontend
        if element['denomination'] and '/' in element['denomination']:
            parts = element['denomination'].split('/')
            display = f"{parts[0].strip()} + {parts[1].strip()}"
            if len(parts) > 2:
                display += f" + {parts[2].strip()}"
            print(f"    -> Affichage: {display}")

if __name__ == "__main__":
    simulate_api_response()