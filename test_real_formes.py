"""
Test pour récupérer les vraies formes de chaque univers
"""
import requests
import json

def test_universe_formes():
    universes = ['mundo', 'fruity', 'trigga', 'roaster', 'sunshine']
    
    print("=== VRAIES FORMES PAR UNIVERS ===\n")
    
    for universe in universes:
        try:
            url = f"http://localhost:8888/api/universe/{universe}/formes"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    print(f"🌍 {universe.upper()}")
                    print(f"   Type: {data['type']}")
                    print(f"   Description: {data['description']}")
                    print(f"   Nombre de formes: {data['total_formes']}")
                    print(f"   Formes: {data['formes']}")
                    print()
                else:
                    print(f"❌ {universe}: {data.get('error', 'Erreur inconnue')}")
            else:
                print(f"❌ {universe}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {universe}: {str(e)}")

if __name__ == "__main__":
    test_universe_formes()