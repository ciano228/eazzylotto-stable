import requests

try:
    response = requests.get("http://localhost:8001/api/formes/real/mundo")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erreur: {e}")