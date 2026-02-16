#!/usr/bin/env python3
"""
Test complet du système de session avec analyse temporelle géométrique
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from test_session_service import TestSessionService
from temporal_geometric_service import TemporalGeometricService
import json

def test_complete_session():
    """Test complet avec session_test_001"""
    
    print("🚀 TEST COMPLET SESSION LOTO HEBDOMADAIRE")
    print("=" * 60)
    
    # 1. Créer le service de session
    session_service = TestSessionService({})
    
    # 2. Créer la session de test
    print("📅 Création de la session session_test_001...")
    session_data = session_service.create_test_session("session_test_001", 6)
    
    print(f"✅ Session créée:")
    print(f"   - Nom: {session_data['session_name']}")
    print(f"   - Périodes: {session_data['periods']} semaines")
    print(f"   - Lotos: {', '.join(session_data['loto_names'])}")
    print(f"   - Total tirages: {len(session_data['draws'])}")
    print()
    
    # 3. Afficher quelques exemples de tirages
    print("🎲 EXEMPLES DE TIRAGES GÉNÉRÉS:")
    print("-" * 40)
    
    for i, draw in enumerate(session_data['draws'][:10]):
        print(f"P{draw['period']} - {draw['loto_name']:15} : {draw['numbers']} ({draw['date']})")
    
    if len(session_data['draws']) > 10:
        print(f"... et {len(session_data['draws']) - 10} autres tirages")
    print()
    
    # 4. Analyser avec le service temporel géométrique
    print("🔍 ANALYSE TEMPORELLE GÉOMÉTRIQUE:")
    print("-" * 40)
    
    # Convertir au format attendu
    formatted_draws = []
    for draw in session_data['draws']:
        formatted_draws.append({
            'id': draw['id'],
            'date': draw['date'],
            'numbers': draw['numbers'],
            'universe': 'mundo',
            'loto_name': draw['loto_name'],
            'period': draw['period']
        })
    
    # Analyser
    temporal_service = TemporalGeometricService({})
    
    period_config = {
        'period_type': 'weekly',
        'analyze_by_period': True,
        'session_name': 'session_test_001'
    }
    
    analysis = temporal_service.analyze_temporal_patterns(
        'mundo', formatted_draws, period_config
    )
    
    if 'error' in analysis:
        print(f"❌ Erreur d'analyse: {analysis['error']}")
        return
    
    # 5. Afficher les résultats
    print("📊 RÉSULTATS DE L'ANALYSE:")
    print(f"   - Total tirages analysés: {analysis['total_draws']}")
    print(f"   - Total combinaisons: {analysis['total_combinations']}")
    print(f"   - Mappings géométriques: {len(analysis.get('geometric_mappings', []))}")
    print()
    
    # Patterns récurrents
    recurring = analysis.get('recurring_patterns', [])
    if recurring:
        print(f"🔄 PATTERNS RÉCURRENTS ({len(recurring)}):")
        for i, pattern in enumerate(recurring[:5], 1):
            print(f"  {i}. Position {pattern['position']} - {pattern['description']}")
            print(f"     Confiance: {pattern['confidence']:.1f}% | {pattern['details']}")
        print()
    
    # Patterns temporels
    temporal_patterns = analysis.get('temporal_patterns', [])
    if temporal_patterns:
        print(f"⏰ PATTERNS TEMPORELS ({len(temporal_patterns)}):")
        for i, pattern in enumerate(temporal_patterns[:5], 1):
            print(f"  {i}. {pattern['type']} - {pattern['description']}")
            print(f"     Confiance: {pattern['confidence']:.1f}% | {pattern['details']}")
        print()
    
    # Zones chaudes
    hot_zones = analysis.get('hot_zones', [])
    if hot_zones:
        print(f"🔥 ZONES CHAUDES ({len(hot_zones)}):")
        for i, zone in enumerate(hot_zones[:3], 1):
            print(f"  {i}. {zone['area_name']} - {zone['description']}")
            print(f"     Activité: {zone['frequency']:.1%} | {zone['details']}")
        print()
    
    # Prédictions
    predictions = analysis.get('predictions', [])
    if predictions:
        print(f"🔮 PRÉDICTIONS ({len(predictions)}):")
        for i, pred in enumerate(predictions[:3], 1):
            print(f"  {i}. {pred['description']}")
            print(f"     Confiance: {pred['confidence']:.1f}% | {pred['details']}")
        print()
    
    # Résumé
    summary = analysis.get('summary', {})
    if summary:
        print("📋 RÉSUMÉ EXÉCUTIF:")
        print(f"  • Qualité de l'analyse: {summary.get('analysis_quality', 'N/A')}")
        print(f"  • Position la plus active: {summary.get('most_active_position', 'N/A')}")
        print(f"  • Zone la plus active: {summary.get('most_active_zone', 'N/A')}")
        print(f"  • Patterns haute confiance: {summary.get('high_confidence_recurrences', 0)}")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print("  • Recommandations:")
            for rec in recommendations:
                print(f"    - {rec}")
    
    # 6. Analyser les patterns par loto
    print("\n🎯 ANALYSE PAR LOTO:")
    print("-" * 25)
    
    loto_stats = {}
    for draw in session_data['draws']:
        loto = draw['loto_name']
        if loto not in loto_stats:
            loto_stats[loto] = {'count': 0, 'numbers': []}
        loto_stats[loto]['count'] += 1
        loto_stats[loto]['numbers'].extend(draw['numbers'])
    
    for loto, stats in loto_stats.items():
        unique_numbers = len(set(stats['numbers']))
        avg_per_draw = len(stats['numbers']) / stats['count']
        print(f"  {loto:15} : {stats['count']} tirages, {unique_numbers} numéros uniques, {avg_per_draw:.1f} moy/tirage")
    
    print("\n✅ Test complet terminé avec succès!")
    print("\n💡 PROCHAINES ÉTAPES:")
    print("1. Démarrer le serveur: python simple_server.py")
    print("2. Ouvrir: http://localhost:8881/frontend/katula-temporal-analysis.html")
    print("3. Cliquer 'Créer Session Test' pour voir l'interface complète")

def test_api_integration():
    """Test d'intégration avec l'API"""
    print("\n🌐 TEST INTÉGRATION API")
    print("=" * 30)
    
    import requests
    
    try:
        # Test création session
        session_url = "http://localhost:8881/api/test-session/create"
        session_data = {
            "session_name": "session_test_001",
            "periods": 6
        }
        
        print(f"📡 Test création session: {session_url}")
        response = requests.post(session_url, json=session_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Session créée via API!")
            print(f"   Total tirages: {result.get('total_draws', 0)}")
            
            # Test analyse
            analysis_url = f"http://localhost:8881/api/test-session/session_test_001/analyze/mundo"
            print(f"📊 Test analyse: {analysis_url}")
            
            analysis_response = requests.get(analysis_url, timeout=15)
            
            if analysis_response.status_code == 200:
                analysis_result = analysis_response.json()
                print("✅ Analyse terminée via API!")
                
                analysis = analysis_result.get('analysis', {})
                print(f"   Patterns récurrents: {len(analysis.get('recurring_patterns', []))}")
                print(f"   Zones chaudes: {len(analysis.get('hot_zones', []))}")
                print(f"   Prédictions: {len(analysis.get('predictions', []))}")
            else:
                print(f"⚠️ Erreur analyse: {analysis_response.status_code}")
        else:
            print(f"⚠️ Erreur création session: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API non disponible - Démarrez le serveur avec: python simple_server.py")
    except Exception as e:
        print(f"❌ Erreur API: {e}")

if __name__ == "__main__":
    print("🎲 DÉMARRAGE TEST SESSION COMPLÈTE")
    print()
    
    # Test 1: Session locale
    test_complete_session()
    
    # Test 2: Intégration API (optionnel)
    test_api_integration()
    
    print("\n🎉 Tous les tests terminés!")