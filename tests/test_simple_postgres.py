import requests

API_BASE = "http://localhost:8002/api"

print("=== TEST POSTGRESQL ===")

# Test Health
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"Health: OK - {response.json()}")
except Exception as e:
    print(f"Health: ERREUR - {e}")
    exit()

# Test Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo")
    if response.status_code == 200:
        data = response.json()
        print(f"Mundo: OK - {len(data['formes'])} formes")
        print(f"Formes: {data['formes']}")
    else:
        print(f"Mundo: ERREUR {response.status_code}")
except Exception as e:
    print(f"Mundo: ERREUR - {e}")

# Test Chip 1
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo/chip/1")
    if response.status_code == 200:
        data = response.json()
        print(f"Chip 1: OK - {data['total_items']} items")
    else:
        print(f"Chip 1: ERREUR {response.status_code}")
except Exception as e:
    print(f"Chip 1: ERREUR - {e}")

print("\nPostgreSQL katooling_main_system: OPERATIONNEL")
print("Utilisez: API_BASE = 'http://localhost:8002/api'")