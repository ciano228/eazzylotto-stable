#!/usr/bin/env python3
"""
Test de l'ordre métier appliqué aux formes composées
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_ordre_metier():
    print("=== TEST ORDRE METIER FORMES COMPOSEES ===")
    
    try:
        service = KatulaCompleteService()
        
        # Test trigga
        config = service.get_universe_config('trigga')
        print(f"\nTRIGGA - {len(config.forms)} formes:")
        for i, forme in enumerate(config.forms, 1):
            print(f"  {i:2d}. {forme}")
        
        # Test sunshine  
        config = service.get_universe_config('sunshine')
        print(f"\nSUNSHINE - {len(config.forms)} formes:")
        for i, forme in enumerate(config.forms, 1):
            print(f"  {i:2d}. {forme}")
        
        # Test roaster
        config = service.get_universe_config('roaster')
        print(f"\nROASTER - {len(config.forms)} formes:")
        for i, forme in enumerate(config.forms, 1):
            print(f"  {i:2d}. {forme}")
            
        # Test avec un chip trigga
        print(f"\n=== TEST CHIP 1 TRIGGA ===")
        result = service.get_chip_compartments('trigga', 1)
        if 'error' not in result:
            for compartment in result.get('compartments', []):
                position = compartment['position']
                forme = compartment['forme']
                denomination = compartment['denomination']
                print(f"  Position {position:2d}: {forme:20s} -> {denomination}")
                
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_ordre_metier()