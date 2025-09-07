import requests

API_BASE = "http://localhost:8002"

print("=== DEBUG ENDPOINTS ===")

# Test endpoints disponibles
endpoints = [
    "/api/health",
    "/api/formes/real/mundo", 
    "/katula/table/mundo",
    "/analytics/katula/table/mundo"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"  OK: {list(response.json().keys())}")
    except Exception as e:
        print(f"{endpoint}: ERREUR - {e}")