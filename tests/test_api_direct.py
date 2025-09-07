import requests
import json

API_BASE = "http://localhost:8001/api"

# Test 1: Health check
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"Health: {response.status_code} - {response.json()}")
except:
    print("Serveur non demarré")

# Test 2: Formes Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo")
    if response.status_code == 200:
        data = response.json()
        print(f"Mundo formes: {data['formes'][:5]}")
    else:
        print(f"Erreur formes: {response.status_code}")
except Exception as e:
    print(f"Erreur: {e}")

# Test 3: Chip 1 Mundo
try:
    response = requests.get(f"{API_BASE}/formes/real/mundo/chip/1")
    if response.status_code == 200:
        data = response.json()
        print(f"Chip 1: {data}")
    else:
        print(f"Erreur chip: {response.status_code}")
except Exception as e:
    print(f"Erreur chip: {e}")