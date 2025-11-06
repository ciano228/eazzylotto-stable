#!/usr/bin/env python3
"""
Test de l'interface katula-dynamic.html avec les nouvelles routes API
"""

import requests
import json
import time

def test_katula_api():
    """Test des nouvelles routes API Katula"""
    base_url = "http://localhost:8000/api"
    
    print("🚀 Test des routes API Katula")
    print("=" * 50)
    
    # Test 1: Route principale de données
    print("\n1. Test route principale /katula/data/fruity")
    try:
        response = requests.get(f"{base_url}/katula/data/fruity", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('status', 'N/A')}")
            print(f"   📊 Chips trouvés: {data.get('total_chips', 0)}")
            print(f"   🌍 Univers: {data.get('universe', 'N/A')}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Route des formes
    print("\n2. Test route formes /katula/data/fruity/formes")
    try:
        response = requests.get(f"{base_url}/katula/data/fruity/formes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {len(data.get('formes', []))} formes")
            print(f"   📋 Formes: {data.get('formes', [])}")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Route granque-tome
    print("\n3. Test route granque-tome /katula/data/fruity/granque-tome")
    try:
        response = requests.get(f"{base_url}/katula/data/fruity/granque-tome", timeout=10)
        if response.status_code == 200:
            data = response.json()
            granques = len(data.get('granque_data', {}))
            tomes = len(data.get('tome_data', {}))
            print(f"   ✅ Succès: {granques} granques, {tomes} tomes")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Route chip spécifique
    print("\n4. Test route chip /katula/data/fruity/chip/1")
    try:
        response = requests.get(f"{base_url}/katula/data/fruity/chip/1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_items = data.get('total_items', 0)
            print(f"   ✅ Succès: {total_items} éléments dans chip 1")
        else:
            print(f"   ❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Instructions pour tester l'interface:")
    print("   1. Ouvrez frontend/katula-dynamic.html dans votre navigateur")
    print("   2. Sélectionnez un univers (ex: fruity)")
    print("   3. Cliquez sur 'Charger Univers'")
    print("   4. Les données réelles de la BD devraient s'afficher")

if __name__ == "__main__":
    test_katula_api()
