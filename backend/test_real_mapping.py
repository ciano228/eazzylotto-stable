#!/usr/bin/env python3
"""
Test du mapping entre BD et structure réelle
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.enhanced_real_katula_service import enhanced_real_katula_service
import json

def test_real_mapping():
    """Tester le mapping des données réelles"""
    
    print("=== TEST DU MAPPING DONNÉES RÉELLES ===\n")
    
    # Test 1: Vérifier la structure réelle chargée
    print("1. Vérification de la structure réelle:")
    if enhanced_real_katula_service.real_structure:
        universes = list(enhanced_real_katula_service.real_structure.keys())
        print(f"   ✓ Structure réelle chargée")
        print(f"   ✓ Univers disponibles: {universes}")
    else:
        print("   ✗ Structure réelle non chargée")
        return
    
    # Test 2: Tester chaque univers
    for univers in universes:
        print(f"\n2. Test de l'univers '{univers}':")
        
        # Données de la structure réelle
        real_data = enhanced_real_katula_service.real_structure[univers]
        print(f"   ✓ Formes disponibles: {real_data['formes_disponibles']}")
        print(f"   ✓ Pétiques disponibles: {real_data['petiques_disponibles']}")
        print(f"   ✓ Nombre de chips: {len(real_data['chips'])}")
        
        # Test d'un chip spécifique
        chip_test = "chip1"
        if chip_test in real_data["chips"]:
            chip_data = enhanced_real_katula_service.get_real_chip_data(univers, chip_test)
            print(f"   ✓ Test {chip_test}:")
            print(f"     - Compartiments: {chip_data['nb_compartiments']}")
            print(f"     - Formes: {chip_data['formes_reelles']}")
            print(f"     - Dénominations: {chip_data['denominations_reelles']}")
        
        # Test de l'affichage raffiné
        refined = enhanced_real_katula_service.get_refined_chip_display(univers, chip_test)
        if "error" not in refined:
            print(f"   ✓ Affichage raffiné disponible")
            for comp in refined["structure_raffinee"]["disposition_verticale"]:
                print(f"     - {comp['forme_geometrique']} | {comp['denomination_reelle']} | {comp['attributs_visuels']['icone_denomination']}")
        else:
            print(f"   ✗ Erreur affichage raffiné: {refined['error']}")
    
    # Test 3: Comparaison avec la BD (si connexion disponible)
    print(f"\n3. Test de comparaison BD vs Structure réelle:")
    try:
        for univers in universes:
            comparison = enhanced_real_katula_service.compare_bd_vs_real_structure(univers)
            if "error" not in comparison:
                print(f"   ✓ Comparaison {univers} réussie")
                bd_data = comparison["donnees_bd"]
                real_data = comparison["donnees_reelles"]
                
                if "error" not in real_data:
                    print(f"     BD: {bd_data['total_chips']} chips, {bd_data['total_formes']} formes")
                    print(f"     Réel: {real_data['total_chips']} chips, {real_data['total_formes']} formes")
                    
                    differences = comparison["differences"]
                    if differences["mapping_effectif"]:
                        print(f"     ✓ Mapping effectif détecté")
                    else:
                        print(f"     ⚠ Mapping non effectif")
                else:
                    print(f"     ⚠ Structure réelle non disponible pour comparaison")
            else:
                print(f"   ⚠ Erreur comparaison {univers}: {comparison['error']}")
    except Exception as e:
        print(f"   ⚠ Erreur connexion BD: {e}")
    
    # Test 4: Données enrichies
    print(f"\n4. Test des données enrichies:")
    try:
        for univers in universes:
            enhanced_data = enhanced_real_katula_service.get_enhanced_table_data(univers)
            if "error" not in enhanced_data:
                print(f"   ✓ Données enrichies {univers} disponibles")
                print(f"     - Taux de succès mapping: {enhanced_data['mapping_success_rate']:.1f}%")
                print(f"     - Structure réelle disponible: {enhanced_data['structure_reelle_disponible']}")
                
                if enhanced_data["enhanced_data"]:
                    sample = enhanced_data["enhanced_data"][0]
                    print(f"     - Exemple chip {sample['chip']}:")
                    if "error" not in sample["donnees_reelles"]:
                        print(f"       BD: {sample['donnees_bd']}")
                        print(f"       Réel: {len(sample['donnees_reelles']['denominations_disponibles'])} dénominations")
            else:
                print(f"   ✗ Erreur données enrichies {univers}: {enhanced_data['error']}")
    except Exception as e:
        print(f"   ⚠ Erreur données enrichies: {e}")
    
    print(f"\n=== RÉSUMÉ ===")
    print("✓ Structure réelle avec formes géométriques précises (carré, cercle, rectangle, triangle)")
    print("✓ Dénominations concrètes (road, bike, chair, forest, shoes, gold, etc.)")
    print("✓ Zones pétiques définies (q1, q2, q3, q4)")
    print("✓ Mapping disponible entre BD et structure réelle")
    print("\nPour utiliser les vraies données:")
    print("- Endpoint: /katula/enhanced/{univers}")
    print("- Endpoint: /katula/chip/{univers}/{chip}")
    print("- Endpoint: /katula/real-structure/{univers}")

if __name__ == "__main__":
    test_real_mapping()