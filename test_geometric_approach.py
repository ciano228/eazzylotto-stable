#!/usr/bin/env python3
"""
Test de l'approche d'analyse temporelle géométrique Katula
Démontre le mapping des tirages sur la table géométrique
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from temporal_geometric_service import TemporalGeometricService
from datetime import datetime, timedelta
import json

def test_geometric_mapping():
    """Test du mapping géométrique avec l'exemple du prompt"""
    
    print("🔍 TEST ANALYSE TEMPORELLE GÉOMÉTRIQUE KATULA")
    print("=" * 60)
    
    # Initialiser le service
    service = TemporalGeometricService({})
    
    # Exemple du prompt : tirage 80-72-89-50-26
    test_draw = {
        'id': 'TEST_001',
        'date': '2024-01-15',
        'numbers': [80, 72, 89, 50, 26],
        'universe': 'mundo'
    }
    
    print(f"📊 Tirage d'exemple: {test_draw['numbers']}")
    print(f"📅 Date: {test_draw['date']}")
    print(f"🌍 Univers: {test_draw['universe']}")
    print()
    
    # 1. Générer les combinaisons 2 à 2
    combinations = service._generate_combinations_from_draw(test_draw['numbers'])
    print(f"🔢 Combinaisons 2 à 2 générées: {len(combinations)}")
    for i, combo in enumerate(combinations, 1):
        print(f"  {i:2d}. {combo[0]:2d} - {combo[1]:2d}")
    print()
    
    # 2. Mapper chaque combinaison à sa position géométrique
    print("🗺️  MAPPING GÉOMÉTRIQUE SUR LA TABLE KATULA")
    print("-" * 50)
    
    geometric_mapping = service._map_combinations_to_geometry(
        test_draw['universe'], combinations, test_draw['date']
    )
    
    if geometric_mapping:
        for i, pos in enumerate(geometric_mapping, 1):
            print(f"{i:2d}. Combinaison {pos['combination'][0]}-{pos['combination'][1]}:")
            print(f"    → Position géométrique: {pos['geometric_position']['coordinates']}")
            print(f"    → Ligne {pos['geometric_position']['ligne']}, Colonne {pos['geometric_position']['colonne']}")
            print(f"    → Quadrant: {pos['quadrant']}")
            print(f"    → Zone: {pos['zone']}")
            print(f"    → Dénomination: {pos['denomination']}")
            if pos.get('attributes'):
                print(f"    → Tome: {pos['attributes']['tome']}")
                print(f"    → Granque: {pos['attributes']['granque']}")
                print(f"    → Forme: {pos['attributes']['forme']}")
            print()
    else:
        print("❌ Aucun mapping géométrique généré")
        return
    
    # 3. Analyser plusieurs tirages pour détecter les patterns
    print("📈 ANALYSE DES PATTERNS TEMPORELS")
    print("-" * 40)
    
    # Générer plusieurs tirages de test
    test_draws = []
    base_date = datetime.strptime(test_draw['date'], '%Y-%m-%d')
    
    # Ajouter le tirage principal
    test_draws.append(test_draw)
    
    # Générer 5 tirages supplémentaires
    for i in range(1, 6):
        date = base_date + timedelta(days=i*7)  # Un tirage par semaine
        numbers = generate_test_draw(i)
        
        test_draws.append({
            'id': f'TEST_{i+1:03d}',
            'date': date.strftime('%Y-%m-%d'),
            'numbers': numbers,
            'universe': 'mundo'
        })
    
    print(f"📊 Analyse de {len(test_draws)} tirages:")
    for draw in test_draws:
        print(f"  {draw['id']}: {draw['numbers']} ({draw['date']})")
    print()
    
    # 4. Analyser les patterns
    period_config = {
        'period_type': 'weekly',
        'analyze_by_period': True
    }
    
    analysis = service.analyze_temporal_patterns(
        test_draw['universe'], test_draws, period_config
    )
    
    if 'error' in analysis:
        print(f"❌ Erreur d'analyse: {analysis['error']}")
        return
    
    # 5. Afficher les résultats
    print("🎯 RÉSULTATS DE L'ANALYSE")
    print("-" * 30)
    
    print(f"Total tirages analysés: {analysis['total_draws']}")
    print(f"Total combinaisons: {analysis['total_combinations']}")
    print()
    
    # Patterns récurrents
    recurring = analysis.get('recurring_patterns', [])
    if recurring:
        print(f"🔄 PATTERNS RÉCURRENTS ({len(recurring)}):")
        for i, pattern in enumerate(recurring[:5], 1):
            print(f"  {i}. Position {pattern['position']} - {pattern['description']}")
            print(f"     Confiance: {pattern['confidence']:.1f}% - {pattern['details']}")
        print()
    
    # Zones chaudes
    hot_zones = analysis.get('hot_zones', [])
    if hot_zones:
        print(f"🔥 ZONES CHAUDES ({len(hot_zones)}):")
        for i, zone in enumerate(hot_zones[:3], 1):
            print(f"  {i}. {zone['area_name']} - {zone['description']}")
            print(f"     Activité: {zone['frequency']:.1%} - {zone['details']}")
        print()
    
    # Prédictions
    predictions = analysis.get('predictions', [])
    if predictions:
        print(f"🔮 PRÉDICTIONS ({len(predictions)}):")
        for i, pred in enumerate(predictions[:3], 1):
            print(f"  {i}. {pred['description']}")
            print(f"     Confiance: {pred['confidence']:.1f}% - {pred['details']}")
        print()
    
    # Résumé
    summary = analysis.get('summary', {})
    if summary:
        print("📋 RÉSUMÉ DE L'ANALYSE:")
        print(f"  Qualité de l'analyse: {summary.get('analysis_quality', 'N/A')}")
        print(f"  Position la plus active: {summary.get('most_active_position', 'N/A')}")
        print(f"  Zone la plus active: {summary.get('most_active_zone', 'N/A')}")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print("  Recommandations:")
            for rec in recommendations:
                print(f"    • {rec}")
    
    print("\n✅ Test terminé avec succès!")

def generate_test_draw(seed):
    """Génère un tirage de test basé sur une seed"""
    import random
    random.seed(seed * 42)  # Seed fixe pour reproductibilité
    
    numbers = []
    while len(numbers) < 5:
        num = random.randint(1, 90)
        if num not in numbers:
            numbers.append(num)
    
    return sorted(numbers)

def test_api_integration():
    """Test d'intégration avec l'API"""
    print("\n🌐 TEST INTÉGRATION API")
    print("=" * 30)
    
    import requests
    
    # Test de l'endpoint de mapping géométrique
    api_url = "http://localhost:8881/api/analytics/geometric-mapping/mundo"
    test_data = {
        "numbers": [80, 72, 89, 50, 26],
        "date": "2024-01-15"
    }
    
    try:
        print(f"📡 Test API: {api_url}")
        print(f"📊 Données: {test_data}")
        
        response = requests.post(api_url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API disponible!")
            print(f"   Status: {result.get('status')}")
            print(f"   Positions géométriques: {len(result.get('geometric_positions', []))}")
            print(f"   Quadrants: {result.get('summary', {}).get('quadrants', [])}")
        else:
            print(f"⚠️  API répond avec status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API non disponible - Démarrez le serveur avec: python simple_server.py")
    except Exception as e:
        print(f"❌ Erreur API: {e}")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS")
    print()
    
    # Test 1: Mapping géométrique local
    test_geometric_mapping()
    
    # Test 2: Intégration API (optionnel)
    test_api_integration()
    
    print("\n🎉 Tous les tests terminés!")
    print("\n💡 UTILISATION:")
    print("1. Démarrez le serveur: python simple_server.py")
    print("2. Ouvrez: http://localhost:8881/frontend/katula-temporal-analysis.html")
    print("3. Cliquez sur 'Test Mapping Géométrique' pour tester avec [80,72,89,50,26]")