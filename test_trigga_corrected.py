#!/usr/bin/env python3
"""
Test de trigga avec la configuration corrigée
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_trigga_corrected():
    print("=== TEST TRIGGA CORRIGE ===")
    
    try:
        service = KatulaCompleteService()
        
        # Vérifier la configuration
        config = service.get_universe_config('trigga')
        print(f"Formes configurées: {len(config.forms)}")
        for i, forme in enumerate(config.forms, 1):
            print(f"  {i:2d}. {forme}")
        
        # Tester un chip
        result = service.get_chip_compartments('trigga', 1)
        
        print(f"\nChip 1 trigga - {result.get('total_compartments', 0)} compartiments:")
        if 'error' not in result:
            for compartment in result.get('compartments', []):
                position = compartment['position']
                forme = compartment['forme']
                denomination = compartment['denomination']
                
                print(f"  Position {position:2d}: {forme:20s} -> {denomination}")
                
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_trigga_corrected()