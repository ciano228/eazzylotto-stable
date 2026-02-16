#!/usr/bin/env python3
"""
Test direct du chip 48 de mundo pour vérifier les dénominations multiples
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_chip48():
    print("=== TEST CHIP 48 MUNDO ===")
    
    try:
        service = KatulaCompleteService()
        result = service.get_chip_compartments('mundo', 48)
        
        print(f"Résultat brut: {result}")
        
        if 'error' in result:
            print(f"❌ Erreur: {result['error']}")
            return
        
        print(f"\n📊 Chip 48 - {result.get('total_compartments', 0)} compartiments:")
        
        for compartment in result.get('compartments', []):
            forme = compartment['forme']
            denomination = compartment['denomination']
            position = compartment['position']
            
            print(f"  Position {position}: {forme} -> '{denomination}'")
            
            if denomination and '/' in denomination:
                print(f"    ✅ DÉNOMINATION MULTIPLE DÉTECTÉE: {denomination}")
            elif denomination == "---":
                print(f"    ⚪ Tiroir vide")
            else:
                print(f"    ⚫ Dénomination simple: {denomination}")
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chip48()