#!/usr/bin/env python3
"""
Test rapide du chargement des matrices Katula
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.katula_table_service import KatulaTableService

def test_matrix_creation():
    """Test création matrice de base"""
    print("=== Test création matrice ===")
    table = KatulaTableService.create_katula_table("mundo")
    
    print(f"Univers: {table['universe']}")
    print(f"Dimensions: {table['dimensions']}")
    print(f"Total chips: {len(table['chip_positions'])}")
    
    # Vérifier structure
    assert table['dimensions']['total_chips'] == 48
    assert len(table['matrix']) == 8
    assert len(table['matrix'][0]) == 6
    print("✓ Structure matrice OK")

def test_neighbors():
    """Test voisinage"""
    print("\n=== Test voisinage ===")
    
    # Test chip central
    neighbors = KatulaTableService.get_chip_neighbors(20)
    print(f"Chip 20 voisins: {neighbors['neighbors']}")
    assert len(neighbors['neighbors']) == 8  # Chip central = 8 voisins
    
    # Test chip coin
    neighbors = KatulaTableService.get_chip_neighbors(1)
    print(f"Chip 1 voisins: {neighbors['neighbors']}")
    assert len(neighbors['neighbors']) == 3  # Coin = 3 voisins
    print("✓ Voisinage OK")

def test_optimal_positions():
    """Test positions optimales"""
    print("\n=== Test positions optimales ===")
    optimal = KatulaTableService.find_optimal_positions("mundo")
    print(f"Positions optimales: {optimal}")
    assert len(optimal) == 8
    assert 1 in optimal and 48 in optimal  # Coins
    print("✓ Positions optimales OK")

def test_distances():
    """Test matrice distances (échantillon)"""
    print("\n=== Test distances ===")
    distances = KatulaTableService.calculate_distance_matrix()
    
    # Test quelques distances
    d1_2 = distances['chip1']['chip2']
    d1_48 = distances['chip1']['chip48']
    
    print(f"Distance chip1->chip2: {d1_2}")
    print(f"Distance chip1->chip48: {d1_48}")
    
    assert d1_2 == 1.0  # Voisins horizontaux
    assert d1_48 > 8.0  # Coins opposés
    print("✓ Distances OK")

if __name__ == "__main__":
    try:
        test_matrix_creation()
        test_neighbors()
        test_optimal_positions()
        test_distances()
        print("\n🎉 TOUS LES TESTS PASSENT")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)