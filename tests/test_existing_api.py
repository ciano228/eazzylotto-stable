#!/usr/bin/env python3
"""
Test des routes API existantes pour katula-dynamic.html
"""

import requests
import json

def test_existing_routes():
    """Test des routes API existantes"""
    base_url = "http://localhost:8000/api"
    
    print("🚀 Test des routes API existantes")
    print("=" * 50)
    
    # Test 1: Route table
    print("\n1. Test /katula/table/fruity")
    try:
        response = requests.get(f"{base_url}/katula/table/fruity", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('status', 'N/A')}")
            if 'data' in data:
                print(f"   📊 Chips: {data['data'].get('total_chips', 0)}")
                print(f"   🌍 Univers: {data['data'].get('universe', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Route formes
    print("\n2. Test /katula/formes/fruity")
    try:
        response = requests.get(f"{base_url}/katula/formes/fruity", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('status', 'N/A')}")
            if 'formes' in data:
                print(f"   📋 Formes: {len(data['formes'])}")
                for forme in data['formes']:
                    print(f"      - {forme.get('id', 'N/A')}: {forme.get('name', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Route chip
    print("\n3. Test /katula/chip/fruity/1")
    try:
        response = requests.get(f"{base_url}/katula/chip/fruity/1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('status', 'N/A')}")
            if 'data' in data:
                print(f"   📦 Chip 1: {len(data['data'].get('formes_data', {}))} formes")
        else:
            print(f"   ❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Interface prête ! Ouvrez frontend/katula-dynamic.html")

if __name__ == "__main__":
    test_existing_routes()
