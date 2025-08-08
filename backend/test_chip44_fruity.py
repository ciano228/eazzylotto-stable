#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.services.forme_service import FormeService

def test_chip44_fruity():
    db = next(get_db())
    
    print('=== TEST CHIP 44 FRUITY - DONNÉES BRUTES ===')
    chip_data = FormeService.get_chip_formes('fruity', 44, db)
    
    print(f"Univers: {chip_data['universe']}")
    print(f"Chip: {chip_data['chip_number']}")
    print(f"Total formes: {chip_data['total_formes']}")
    print("\nDétail des formes:")
    
    for forme, items in chip_data['formes_data'].items():
        print(f"\n🎨 {forme.upper()}:")
        denominations = [item['denomination'] for item in items]
        print(f"  Dénominations: {denominations}")
        
        # Simuler ce que fait l'interface
        if len(denominations) == 1:
            display_text = denominations[0]
        elif len(denominations) > 1:
            display_text = '/'.join(denominations)
        else:
            display_text = '---'
            
        print(f"  Affichage interface: '{display_text}'")
        print(f"  Recherche API: '{'/'.join(denominations) if denominations else display_text}'")

if __name__ == "__main__":
    test_chip44_fruity()