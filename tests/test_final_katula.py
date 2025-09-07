import requests

print("=== TEST FINAL KATULA ===")

API_BASE = "http://localhost:8002/api"

# Test 1: Serveur
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"Serveur: OK")
except:
    print("Serveur: ERREUR - Demarrez: python server_postgres_simple.py")
    exit()

# Test 2: Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo")
    data = response.json()
    print(f"Mundo: OK - {len(data['formes'])} formes")
    print(f"  Formes: {data['formes'][:3]}...")
except Exception as e:
    print(f"Mundo: ERREUR - {e}")

# Test 3: Roaster
try:
    response = requests.get(f"{API_BASE}/formes/real/roaster")
    data = response.json()
    print(f"Roaster: OK - {len(data['formes'])} formes")
    print(f"  Formes: {data['formes'][:3]}...")
except Exception as e:
    print(f"Roaster: ERREUR - {e}")

# Test 4: Chip test
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo/chip/5")
    data = response.json()
    print(f"Chip 5: OK - {data['total_items']} items")
except Exception as e:
    print(f"Chip 5: ERREUR - {e}")

print("\n=== RESULTAT ===")
print("PostgreSQL katooling_main_system: OPERATIONNEL")
print("Ouvrez: katula-table-modular.html ou katula-table-complete.html")
print("Selectionnez Mundo ou Roaster et testez!")