#!/usr/bin/env python3
"""
Test de l'ordre métier dans l'UI via simulation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def simulate_ui_data():
    print("=== SIMULATION DONNEES UI MUNDO L8 ===")
    
    try:
        service = KatulaCompleteService()
        
        # Simuler les données pour la ligne 8 (chips 43-48)
        for col in range(1, 7):
            chip_number = (8 - 1) * 6 + col
            
            # Récupérer les données du service (comme l'API)
            result = service.get_chip_compartments('mundo', chip_number)
            
            if 'error' not in result:
                print(f"\nChip {chip_number} (L8C{col}) - Ordre métier:")
                
                # Simuler le traitement frontend avec ordre métier
                formes_data = {}
                for compartment in result.get('compartments', []):
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    if forme and denomination and denomination != "---":
                        formes_data[forme] = [{
                            "denomination": denomination,
                            "frequency": 1,
                            "multiple": '/' in denomination
                        }]
                
                # Ordre métier mundo
                forme_order = ['carre', 'triangle', 'cercle', 'rectangle']
                
                print("  Données API:", formes_data)
                print("  Ordre d'affichage UI:")
                
                for position, forme in enumerate(forme_order, 1):
                    if forme in formes_data:
                        denom = formes_data[forme][0]['denomination']
                        print(f"    Position {position}: {forme:10s} -> {denom}")
                    else:
                        print(f"    Position {position}: {forme:10s} -> ---")
                        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    simulate_ui_data()