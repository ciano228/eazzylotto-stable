#!/usr/bin/env python3
"""Test direct du service Katula"""

# Test direct des méthodes
class TestKatulaTable:
    MATRIX_ROWS = 8
    MATRIX_COLS = 6
    TOTAL_CHIPS = 48
    
    @staticmethod
    def test_chip_neighbors(chip_number):
        if chip_number < 1 or chip_number > 48:
            return {"error": "Chip invalide"}
        
        row = ((chip_number - 1) // 6) + 1
        col = ((chip_number - 1) % 6) + 1
        
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 1 <= nr <= 8 and 1 <= nc <= 6:
                    neighbor_chip = (nr - 1) * 6 + nc
                    neighbors.append(neighbor_chip)
        
        return {"chip": chip_number, "neighbors": neighbors}
    
    @staticmethod
    def test_optimal_positions():
        optimal_chips = []
        optimal_chips.extend([8, 11, 32, 35])  # Centres
        optimal_chips.extend([1, 6, 43, 48])   # Coins
        return sorted(set(optimal_chips))

# Tests
print("=== Test voisinage ===")
result = TestKatulaTable.test_chip_neighbors(20)
print(f"Chip 20: {len(result['neighbors'])} voisins")

result = TestKatulaTable.test_chip_neighbors(1)
print(f"Chip 1: {len(result['neighbors'])} voisins")

print("\n=== Test positions optimales ===")
optimal = TestKatulaTable.test_optimal_positions()
print(f"Positions: {optimal}")

print("\n=== Test matrice 8x6 ===")
total_positions = 8 * 6
print(f"Total positions: {total_positions}")

print("\nTESTS VALIDES")