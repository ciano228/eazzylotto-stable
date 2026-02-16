#!/usr/bin/env python3
"""
Test de l'API pour le chip 38 fruity avec dénominations multiples
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_api_format():
    print("=== TEST FORMAT API CHIP 38 FRUITY ===")
    
    try:
        service = KatulaCompleteService()
        result = service.get_chip_compartments('fruity', 38)
        
        print("Données brutes du service:")
        for compartment in result.get('compartments', []):
            if compartment['denomination'] != '---':
                print(f"  {compartment['forme']}: {compartment['denomination']}")
        
        # Simuler le traitement de l'API
        print("\nTraitement API:")
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
        
        print(f"Données API: {formes_data}")
        
        # Simuler l'affichage frontend
        print("\nAffichage frontend:")
        for forme, denoms in formes_data.items():
            for denom_data in denoms:
                denomination = denom_data['denomination']
                if '/' in denomination:
                    parts = denomination.split('/')
                    display = f"{parts[0].strip()}<br/>{parts[1].strip()}"
                    print(f"  {forme}: {display} (sur 2 lignes)")
                else:
                    print(f"  {forme}: {denomination} (simple)")
                    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_api_format()