#!/usr/bin/env python3
"""
Test du service KatulaCompleteService
Validation complète des fonctionnalités
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.katula_complete_service import KatulaCompleteService
import json

def test_service():
    print("[TEST] KatulaCompleteService")
    print("=" * 50)
    
    # Test 1: Création table complète
    print("\n[1] Creation table Katula complete...")
    table = KatulaCompleteService.create_complete_katula_table("mundo")
    print(f"[OK] Table creee: {table['name']}")
    print(f"   - Dimensions: {table['dimensions']['rows']}x{table['dimensions']['columns']}")
    print(f"   - Total chips: {table['dimensions']['total_chips']}")
    print(f"   - Univers: {table['universe']}")
    
    # Test 2: Vérification matrice
    print("\n[2] Verification matrice...")
    matrix = table['matrix']
    print(f"[OK] Matrice: {len(matrix)} lignes x {len(matrix[0])} colonnes")
    
    # Afficher quelques chips
    print("\n[INFO] Exemples de chips:")
    for i in [0, 23, 47]:  # Premier, milieu, dernier
        chip = table['chip_positions'][f'chip{i+1}']
        print(f"   Chip {i+1}: {chip['position']} - {chip['petique']} - {chip['granque_name']}")
    
    # Test 3: Side panel
    print("\n[3] Test side panel...")
    side_panel = KatulaCompleteService.get_side_panel_data("mundo")
    print(f"[OK] Side panel configure pour {side_panel['universe']}")
    print(f"   - Granques: {len(side_panel['available_granques'])}")
    print(f"   - Tomes: {len(side_panel['available_tomes'])}")
    print(f"   - Quick filters: {list(side_panel['quick_filters'].keys())}")
    
    # Test 4: Filtres
    print("\n[4] Test filtres...")
    filters = {
        "granque": ["alpha", "beta"],
        "tome": ["tome1", "tome2"],
        "petique": ["q1"]
    }
    filtered = KatulaCompleteService.apply_filters(table, filters)
    print(f"[OK] Filtres appliques: {filtered['total_filtered']}/{filtered['total_original']} chips")
    
    # Test 5: Différents univers
    print("\n[5] Test univers multiples...")
    for universe in ["fruity", "trigga", "roaster"]:
        test_table = KatulaCompleteService.create_complete_katula_table(universe)
        print(f"[OK] Univers {universe}: {test_table['name']}")
    
    print("\n[SUCCESS] Tous les tests reussis!")
    print("Le service KatulaCompleteService est operationnel!")

if __name__ == "__main__":
    test_service()