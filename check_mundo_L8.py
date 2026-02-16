#!/usr/bin/env python3
"""
Vérifier l'ordre des icônes sur la ligne 8 de mundo
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def check_mundo_L8():
    print("=== VERIFICATION LIGNE 8 MUNDO ===")
    
    try:
        service = KatulaCompleteService()
        
        # Ligne 8 = chips 43, 44, 45, 46, 47, 48
        for col in range(1, 7):
            chip_number = (8 - 1) * 6 + col  # Ligne 8, colonne col
            
            print(f"\nChip {chip_number} (L8C{col}):")
            result = service.get_chip_compartments('mundo', chip_number)
            
            if 'error' not in result:
                for compartment in result.get('compartments', []):
                    position = compartment['position']
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    status = "VIDE" if denomination == "---" else "DONNEES"
                    print(f"  Position {position}: {forme:10s} -> {denomination:15s} ({status})")
                    
                    # Vérifier l'ordre métier
                    expected_forms = ['carre', 'triangle', 'cercle', 'rectangle']
                    if position <= len(expected_forms):
                        expected_forme = expected_forms[position - 1]
                        if forme != expected_forme:
                            print(f"    *** ERREUR ORDRE: attendu {expected_forme}, trouvé {forme} ***")
            else:
                print(f"  Erreur: {result.get('error', 'Inconnue')}")
                
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_mundo_L8()