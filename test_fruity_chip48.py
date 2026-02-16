#!/usr/bin/env python3
"""
Test du chip 48 de l'univers fruity
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_fruity_chip48():
    print("=== TEST CHIP 48 FRUITY ===")
    
    try:
        service = KatulaCompleteService()
        result = service.get_chip_compartments('fruity', 48)
        
        print(f"Resultat brut: {result}")
        
        if 'error' in result:
            print(f"Erreur: {result['error']}")
            return
        
        print(f"\nChip 48 fruity - {result.get('total_compartments', 0)} compartiments:")
        
        for compartment in result.get('compartments', []):
            forme = compartment['forme']
            denomination = compartment['denomination']
            position = compartment['position']
            
            print(f"  Position {position}: {forme} -> '{denomination}'")
            
            if denomination and '/' in denomination:
                print(f"    MULTIPLE DETECTEE: {denomination}")
                parts = denomination.split('/')
                for i, part in enumerate(parts):
                    print(f"      Partie {i+1}: {part.strip()}")
            elif denomination == "---":
                print(f"    Tiroir vide")
            else:
                print(f"    Simple: {denomination}")
                
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fruity_chip48()