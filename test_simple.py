import requests
import urllib.parse

# Test simple
url = "http://localhost:8881/api/denomination/mundo/table%202"
response = requests.get(url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['status']}")
    print(f"Total: {data['total_combinations']}")
    print("CORRECTION REUSSIE!")
else:
    print("ERREUR")