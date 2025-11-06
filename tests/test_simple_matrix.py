#!/usr/bin/env python3
"""Test simple matrice Katula"""
import sys
import os

# Import direct du service
sys.path.append('backend')
try:
    from app.services.katula_table_service import KatulaTableService
    
    print("=== Test creation matrice ===")
    table = KatulaTableService.create_katula_table("mundo")
    print(f"Univers: {table['universe']}")
    print(f"Total chips: {len(table['chip_positions'])}")
    print(f"Matrice: {len(table['matrix'])}x{len(table['matrix'][0])}")
    
    print("\n=== Test voisinage ===")
    neighbors = KatulaTableService.get_chip_neighbors(20)
    print(f"Chip 20 a {len(neighbors['neighbors'])} voisins")
    
    print("\n=== Test positions optimales ===")
    optimal = KatulaTableService.find_optimal_positions("mundo")
    print(f"Positions optimales: {optimal}")
    
    print("\nTOUS LES TESTS OK")
    
except ImportError as e:
    print(f"Erreur import: {e}")
except Exception as e:
    print(f"Erreur: {e}")