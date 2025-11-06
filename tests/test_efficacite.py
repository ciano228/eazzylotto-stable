#!/usr/bin/env python3
"""
Test d'efficacité EazzyCalculator
Validation complète du système
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8004/api"

def test_api_health():
    """Test de santé de l'API"""
    try:
        response = requests.get(f"{API_BASE}/health")
        return response.status_code == 200 and response.json().get("status") == "healthy"
    except:
        return False

def test_authentication():
    """Test d'authentification"""
    try:
        # Test login
        login_data = {"username": "admin", "password": "admin"}
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token is not None
        return False
    except:
        return False

def test_sessions_endpoint():
    """Test endpoint sessions"""
    try:
        response = requests.get(f"{API_BASE}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            return len(sessions) > 0
        return False
    except:
        return False

def test_analytics_endpoint():
    """Test endpoint analytics"""
    try:
        response = requests.get(f"{API_BASE}/analytics")
        if response.status_code == 200:
            data = response.json()
            return "stats" in data and "totalSessions" in data["stats"]
        return False
    except:
        return False

def test_ml_predictions():
    """Test endpoint ML predictions"""
    try:
        response = requests.get(f"{API_BASE}/ml/predictions")
        if response.status_code == 200:
            data = response.json()
            return "predictions" in data and len(data["predictions"]) > 0
        return False
    except:
        return False

def run_efficiency_tests():
    """Exécution des tests d'efficacité"""
    print("TESTS D'EFFICACITE EAZZYCALCULATOR")
    print("=" * 50)
    
    tests = [
        ("Santé API", test_api_health),
        ("Authentification", test_authentication),
        ("Sessions", test_sessions_endpoint),
        ("Analytics", test_analytics_endpoint),
        ("Prédictions ML", test_ml_predictions)
    ]
    
    results = []
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_func in tests:
        print(f"🔍 Test: {test_name}...", end=" ")
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        if success:
            print(f"✅ RÉUSSI ({end_time - start_time:.2f}s)")
            passed_tests += 1
        else:
            print(f"❌ ÉCHOUÉ ({end_time - start_time:.2f}s)")
        
        results.append({
            "test": test_name,
            "success": success,
            "duration": end_time - start_time
        })
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 50)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
    print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 SYSTÈME HAUTEMENT EFFICACE!")
    elif success_rate >= 60:
        print("✅ SYSTÈME EFFICACE")
    else:
        print("⚠️  SYSTÈME NÉCESSITE DES AMÉLIORATIONS")
    
    print(f"⏱️  Temps total: {sum(r['duration'] for r in results):.2f}s")
    print(f"📅 Testé le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate

if __name__ == "__main__":
    efficiency_rate = run_efficiency_tests()
    exit(0 if efficiency_rate >= 80 else 1)