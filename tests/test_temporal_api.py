#!/usr/bin/env python3
"""
Test rapide de l'API temporelle
"""
import requests
import json

def test_temporal_api():
    base_url = "http://localhost:8000/api/analytics"
    
    print("🔧 Test de l'API temporelle...")
    
    # Test 1: Vérifier si l'endpoint existe
    print("\n1. Test endpoint temporal-periods:")
    try:
        response = requests.get(f"{base_url}/temporal-periods/fruity", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Données: {json.dumps(data, indent=2)}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Test temporal-data
    print("\n2. Test endpoint temporal-data:")
    try:
        url = f"{base_url}/temporal-data/fruity?date_start=2024-01-01&date_end=2024-01-31&marking_type=chip"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Données reçues: {len(data.get('data', {}).get('occurrences', {}))} occurrences")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Vérifier la structure de la BD
    print("\n3. Test structure BD:")
    try:
        # Test simple pour voir si la table existe
        response = requests.get(f"http://localhost:8000/api/analytics/granque-tome/fruity", timeout=5)
        print(f"   Status granque-tome: {response.status_code}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_temporal_api()