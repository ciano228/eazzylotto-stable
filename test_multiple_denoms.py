#!/usr/bin/env python3
"""
Test pour trouver des chips avec dénominations multiples
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_multiple_chips():
    print("=== RECHERCHE DENOMINATIONS MULTIPLES ===")
    
    try:
        service = KatulaCompleteService()
        
        # Tester plusieurs chips
        for chip_num in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 48]:
            result = service.get_chip_compartments('mundo', chip_num)
            
            if 'error' not in result:
                print(f"\nChip {chip_num}:")
                for compartment in result.get('compartments', []):
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    if denomination and denomination != "---":
                        if '/' in denomination:
                            print(f"  *** MULTIPLE: {forme} -> {denomination}")
                        else:
                            print(f"  Simple: {forme} -> {denomination}")
                            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_multiple_chips()