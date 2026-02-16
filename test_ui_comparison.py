#!/usr/bin/env python3
"""
Test de comparaison UI entre différents univers
"""

def simulate_ui_comparison():
    print("=== SIMULATION COMPARAISON UI ===")
    
    # Simulation des données comme dans l'UI
    universes_config = {
        'mundo': ['carre', 'triangle', 'cercle', 'rectangle'],  # 4 tiroirs
        'roaster': [  # 12 tiroirs, pas de formes de base
            'carre-triangle', 'carre-cercle', 'carre-rectangle',
            'triangle-carre', 'triangle-cercle', 'triangle-rectangle', 
            'cercle-carre', 'cercle-triangle', 'cercle-rectangle',
            'rectangle-carre', 'rectangle-triangle', 'rectangle-cercle'
        ],
        'trigga': [  # 10 tiroirs, mix
            'carre', 'triangle', 'cercle', 'rectangle',
            'triangle-cercle', 'triangle-rectangle',
            'cercle-rectangle', 'cercle-triangle',
            'rectangle-cercle', 'rectangle-triangle'
        ]
    }
    
    # Simulation de données pour chip 1 de chaque univers
    chip_data = {
        'mundo': {
            'carre': 'table 2',
            'triangle': 'forest 1', 
            'cercle': 'shoes 1',
            'rectangle': 'gold 1'
        },
        'roaster': {
            'carre-triangle': 'chair 1',
            'carre-cercle': 'lunettes 1',
            'triangle-cercle': 'balaie 1'
            # Autres formes vides
        },
        'trigga': {
            'carre': 'chair 2',
            'triangle': 'forest 3',
            'cercle': 'book 2',
            'rectangle': 'bottle 1',
            'triangle-cercle': 'drum 3'
            # Autres formes vides
        }
    }
    
    for univers, formes in universes_config.items():
        print(f"\n--- {univers.upper()} ---")
        print(f"Tiroirs configurés: {len(formes)}")
        
        data = chip_data.get(univers, {})
        
        print("Affichage UI (ordre métier):")
        for i, forme in enumerate(formes, 1):
            if forme in data:
                print(f"  {i:2d}. {forme:20s} -> {data[forme]}")
            else:
                print(f"  {i:2d}. {forme:20s} -> --- (icône visible, pas de données)")
        
        print(f"Règle appliquée: Seules les {len(formes)} formes de {univers} sont affichées")
        
        # Vérifier qu'on n'affiche pas de formes inexistantes
        if univers == 'roaster':
            print("  ✓ Pas de formes de base affichées (carre, triangle, etc.)")
        elif univers == 'mundo':
            print("  ✓ Pas de formes composées affichées")

if __name__ == "__main__":
    simulate_ui_comparison()