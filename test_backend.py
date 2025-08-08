#!/usr/bin/env python3
"""
Script de test pour vérifier le backend EazzyCalculator
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"

def test_server_status():
    """Test si le serveur répond"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Serveur accessible")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Serveur répond avec le code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Vérifiez que le serveur est démarré avec: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_database_connection():
    """Test la connexion à la base de données via l'API"""
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/universes")
        if response.status_code == 200:
            print("✅ Base de données accessible")
            universes = response.json()
            print(f"   Univers disponibles: {len(universes['universes'])}")
            return True
        else:
            print(f"❌ Problème base de données, code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def test_combination_lookup():
    """Test la recherche d'une combinaison"""
    try:
        # Test avec une combinaison simple
        response = requests.get(f"{BASE_URL}/api/analysis/combinations/1/2")
        if response.status_code == 200:
            print("✅ Recherche de combinaisons fonctionne")
            combo = response.json()
            print(f"   Combinaison 1-2: {combo.get('univers', 'N/A')}")
            return True
        elif response.status_code == 404:
            print("⚠️  Combinaison 1-2 non trouvée (normal si pas dans votre DB)")
            return True
        else:
            print(f"❌ Erreur recherche combinaison: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_create_draw():
    """Test la création d'un tirage"""
    try:
        draw_data = {
            "lottery_name": "Test Loto",
            "draw_date": "17/07/2025",
            "winning_numbers": [1, 15, 23, 45, 67],
            "number_range_min": 1,
            "number_range_max": 90
        }
        
        response = requests.post(f"{BASE_URL}/api/lottery/draws", json=draw_data)
        if response.status_code == 200:
            print("✅ Création de tirage fonctionne")
            result = response.json()
            print(f"   Tirage créé avec ID: {result.get('draw_id')}")
            print(f"   Combinaisons générées: {result.get('total_combinations')}")
            return result.get('draw_id')
        else:
            print(f"❌ Erreur création tirage: {response.status_code}")
            print(f"   Détail: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_analysis(draw_id):
    """Test l'analyse d'un tirage"""
    if not draw_id:
        print("⚠️  Pas de tirage à analyser")
        return False
        
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/draw/{draw_id}")
        if response.status_code == 200:
            print("✅ Analyse de tirage fonctionne")
            analysis = response.json()
            print(f"   Tirages analysés: {analysis['draw_info']['lottery_name']}")
            print(f"   Univers trouvés: {len(analysis.get('universes', {}))}")
            return True
        else:
            print(f"❌ Erreur analyse: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test du backend EazzyCalculator")
    print("=" * 50)
    
    # Tests séquentiels
    tests_passed = 0
    total_tests = 5
    
    # 1. Test serveur
    if test_server_status():
        tests_passed += 1
    
    # 2. Test base de données
    if test_database_connection():
        tests_passed += 1
    
    # 3. Test combinaisons
    if test_combination_lookup():
        tests_passed += 1
    
    # 4. Test création tirage
    draw_id = test_create_draw()
    if draw_id:
        tests_passed += 1
    
    # 5. Test analyse
    if test_analysis(draw_id):
        tests_passed += 1
    
    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {tests_passed}/{total_tests} tests réussis")
    
    if tests_passed == total_tests:
        print("🎉 Tous les tests sont passés ! Le backend fonctionne correctement.")
    elif tests_passed >= 3:
        print("⚠️  La plupart des tests passent. Quelques ajustements peuvent être nécessaires.")
    else:
        print("❌ Plusieurs problèmes détectés. Vérifiez la configuration.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)