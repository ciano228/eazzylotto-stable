"""
Vérifier les vraies formes de chaque univers depuis le service
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def check_universe_formes():
    service = KatulaCompleteService()
    universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    print("=== VRAIES FORMES PAR UNIVERS ===\n")
    
    for universe in universes:
        try:
            config = service.get_universe_config(universe)
            print(f"UNIVERS: {universe.upper()}")
            print(f"   Type: {config.type.value}")
            print(f"   Description: {config.description}")
            print(f"   Nombre de formes: {len(config.forms)}")
            print(f"   Formes: {config.forms}")
            print()
        except Exception as e:
            print(f"ERREUR {universe}: {str(e)}")

if __name__ == "__main__":
    check_universe_formes()