import requests

# Test du serveur sur port 8002
try:
    response = requests.get("http://localhost:8002/api/health", timeout=2)
    print(f"Serveur 8002: {response.json()}")
    
    # Test formes mundo
    response = requests.get("http://localhost:8002/api/formes/real/mundo")
    if response.status_code == 200:
        data = response.json()
        print(f"Mundo OK: {len(data['formes'])} formes")
        print(f"Formes: {data['formes'][:3]}")
    else:
        print(f"Erreur mundo: {response.status_code}")
        
except:
    print("Serveur 8002 non accessible")

# Test du serveur sur port 8001  
try:
    response = requests.get("http://localhost:8001/api/health", timeout=2)
    print(f"Serveur 8001: OK")
except:
    print("Serveur 8001 non accessible")