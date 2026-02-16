#!/usr/bin/env python3
"""
Test spécifique pour roaster (pas de formes de base)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_roaster():
    print("=== TEST ROASTER (PAS DE FORMES DE BASE) ===")
    
    try:
        service = KatulaCompleteService()
        
        # Configuration roaster
        config = service.get_universe_config('roaster')
        print(f"Formes roaster ({len(config.forms)}):")
        for i, forme in enumerate(config.forms, 1):
            print(f"  {i:2d}. {forme}")
        
        # Vérifier qu'il n'y a pas de formes de base
        formes_base = ['carre', 'triangle', 'cercle', 'rectangle']
        has_base_forms = any(forme in config.forms for forme in formes_base)
        
        print(f"\nContient des formes de base: {'OUI' if has_base_forms else 'NON'}")
        
        # Test avec chip 1
        result = service.get_chip_compartments('roaster', 1)
        
        if 'error' not in result:
            print(f"\nChip 1 roaster - {result.get('total_compartments')} tiroirs:")
            
            for compartment in result.get('compartments', []):
                position = compartment['position']
                forme = compartment['forme']
                denomination = compartment['denomination']
                
                status = "DONNEES" if denomination != "---" else "VIDE"
                print(f"  {position:2d}. {forme:20s} -> {denomination:15s} ({status})")
                
                # Vérifier que c'est bien une forme composée
                if '-' not in forme:
                    print(f"    *** ATTENTION: {forme} n'est pas une forme composée ***")
        else:
            print(f"Erreur: {result.get('error')}")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_roaster()