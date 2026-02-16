#!/usr/bin/env python3
"""
Vérifier l'ordre des tiroirs dans fruity
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def check_fruity_order():
    print("=== VERIFICATION ORDRE TIROIRS FRUITY ===")
    
    try:
        service = KatulaCompleteService()
        
        # Tester quelques chips de fruity
        for chip_num in [1, 5, 10]:
            result = service.get_chip_compartments('fruity', chip_num)
            
            print(f"\nChip {chip_num} fruity:")
            if 'error' not in result:
                for compartment in result.get('compartments', []):
                    position = compartment['position']
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    print(f"  Position {position}: {forme} -> {denomination}")
                    
                    # Vérifier si rectangle est en position 3 au lieu de 4
                    if forme == 'rectangle' and position != 4:
                        print(f"    *** PROBLEME: rectangle en position {position} au lieu de 4 ***")
                        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_fruity_order()