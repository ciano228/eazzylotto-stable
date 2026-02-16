#!/usr/bin/env python3
"""
Chercher des chips avec vraiment plusieurs dénominations différentes
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def find_real_multiples():
    print("=== RECHERCHE VRAIES DENOMINATIONS MULTIPLES ===")
    
    try:
        service = KatulaCompleteService()
        
        # Tester tous les chips de fruity
        for chip_num in range(1, 49):
            result = service.get_chip_compartments('fruity', chip_num)
            
            if 'error' not in result and result.get('multiple_denominations_found'):
                print(f"\n*** CHIP {chip_num} FRUITY - MULTIPLES TROUVEES ***")
                for compartment in result.get('compartments', []):
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    if denomination and '/' in denomination:
                        print(f"  {forme}: {denomination}")
                        parts = denomination.split('/')
                        print(f"    -> {len(parts)} denominations: {parts}")
                        
                        # Arrêter après le premier trouvé
                        return chip_num, forme, denomination
                        
    except Exception as e:
        print(f"Erreur: {e}")
        
    return None, None, None

if __name__ == "__main__":
    chip, forme, denom = find_real_multiples()
    if chip:
        print(f"\nTROUVE: Chip {chip}, forme {forme}, denominations: {denom}")
    else:
        print("\nAucune denomination multiple trouvee")