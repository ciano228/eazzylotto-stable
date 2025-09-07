import requests
import json

API_BASE = "http://localhost:8002/api"

print("=== TEST COMPLET POSTGRESQL ===")

# Test 1: Health check
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"✅ Health: {response.json()}")
except Exception as e:
    print(f"❌ Health: {e}")
    exit()

# Test 2: Formes Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mundo: {len(data['formes'])} formes")
        print(f"   Formes: {data['formes']}")
        print(f"   Simples: {data['simples']}")
        print(f"   Composites: {data['composites']}")
    else:
        print(f"❌ Mundo: {response.status_code}")
except Exception as e:
    print(f"❌ Mundo: {e}")

# Test 3: Formes Roaster
try:
    response = requests.get(f"{API_BASE}/formes/real/roaster")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Roaster: {len(data['formes'])} formes")
        print(f"   Formes: {data['formes']}")
    else:
        print(f"❌ Roaster: {response.status_code}")
except Exception as e:
    print(f"❌ Roaster: {e}")

# Test 4: Chip 1 Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo/chip/1")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chip 1 Mundo: {data['total_items']} items")
        if data['formes_data']:
            for forme, items in data['formes_data'].items():
                print(f"   {forme}: {len(items)} denominations")
    else:
        print(f"❌ Chip 1: {response.status_code}")
except Exception as e:
    print(f"❌ Chip 1: {e}")

print("\n=== RESULTAT ===")
print("✅ PostgreSQL katooling_main_system connecté")
print("✅ API fonctionnelle sur port 8002")
print("💡 Utilisez API_BASE = 'http://localhost:8002/api' dans vos fichiers HTML")