#!/usr/bin/env python3
"""
Test rapide de l'API backend
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8000/api"
    
    print("🔧 Test de l'API backend...")
    
    # Test 1: Endpoint granque-tome
    print("\n1. Test granque-tome/fruity:")
    try:
        response = requests.get(f"{base_url}/analytics/granque-tome/fruity")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Granques: {list(data.get('granque_data', {}).keys())}")
            print(f"   Tomes: {list(data.get('tome_data', {}).keys())}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Endpoint katula table
    print("\n2. Test katula/table/fruity:")
    try:
        response = requests.get(f"{base_url}/katula/table/fruity")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Positions: {len(data.get('positions', {}))}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Endpoint formes
    print("\n3. Test formes/fruity:")
    try:
        response = requests.get(f"{base_url}/formes/fruity")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Formes: {data.get('formes', [])}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_api()