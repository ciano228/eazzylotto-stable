#!/usr/bin/env python3
"""
Test des règles métier pour tous les univers
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.katula_complete_service import KatulaCompleteService

def test_regles_univers():
    print("=== TEST REGLES METIER TOUS UNIVERS ===")
    
    try:
        service = KatulaCompleteService()
        
        # Test pour chaque univers
        univers_list = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
        
        for univers in univers_list:
            print(f"\n--- UNIVERS {univers.upper()} ---")
            
            # Configuration de l'univers
            config = service.get_universe_config(univers)
            print(f"Formes configurées ({len(config.forms)}): {config.forms}")
            
            # Test avec le chip 1
            result = service.get_chip_compartments(univers, 1)
            
            if 'error' not in result:
                print("Tiroirs affichés (ordre métier):")
                
                for compartment in result.get('compartments', []):
                    position = compartment['position']
                    forme = compartment['forme']
                    denomination = compartment['denomination']
                    
                    status = "DONNEES" if denomination != "---" else "VIDE"
                    print(f"  {position:2d}. {forme:20s} -> {denomination:15s} ({status})")
                
                # Vérifier que seules les formes de l'univers sont affichées
                displayed_forms = [c['forme'] for c in result.get('compartments', [])]
                expected_forms = config.forms
                
                if displayed_forms == expected_forms:
                    print("  ✓ Ordre métier respecté")
                else:
                    print("  ❌ Problème d'ordre détecté")
                    print(f"    Attendu: {expected_forms}")
                    print(f"    Affiché: {displayed_forms}")
            else:
                print(f"  Erreur: {result.get('error')}")
                
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_regles_univers()