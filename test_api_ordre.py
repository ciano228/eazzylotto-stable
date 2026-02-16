#!/usr/bin/env python3
"""
Test de l'API pour vérifier l'ordre métier dans l'UI
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def simulate_api_call():
    print("=== SIMULATION APPEL API POUR UI ===")
    
    try:
        service = KatulaCompleteService()
        
        # Simuler l'appel API /api/universe/trigga/formes
        config = service.get_universe_config('trigga')
        api_response = {
            "status": "success",
            "universe": "trigga",
            "formes": config.forms,
            "total_formes": len(config.forms),
            "type": config.type.value,
            "description": config.description
        }
        
        print("Réponse API /api/universe/trigga/formes:")
        print(f"  Statut: {api_response['status']}")
        print(f"  Univers: {api_response['universe']}")
        print(f"  Type: {api_response['type']}")
        print(f"  Total formes: {api_response['total_formes']}")
        print("  Formes (ordre métier):")
        
        for i, forme in enumerate(api_response['formes'], 1):
            print(f"    {i:2d}. {forme}")
        
        # Simuler l'appel pour un chip
        print(f"\n=== SIMULATION CHIP API ===")
        chip_result = service.get_chip_compartments('trigga', 1)
        
        if 'error' not in chip_result:
            print("Données chip 1 trigga (ordre métier appliqué):")
            for compartment in chip_result.get('compartments', []):
                position = compartment['position']
                forme = compartment['forme']
                denomination = compartment['denomination']
                if denomination != "---":
                    print(f"  Tiroir {position}: {forme} -> {denomination}")
                    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    simulate_api_call()