#!/usr/bin/env python3
import requests
import time

def test_backend():
    print("🔍 Test de connexion au backend...")
    
    try:
        # Test de base
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend accessible")
            print(f"   Réponse: {response.json()}")
        else:
            print(f"❌ Backend erreur: {response.status_code}")
            
        # Test endpoint Katula
        response = requests.get("http://localhost:8000/api/analytics/katula/table/mundo", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint Katula accessible")
            data = response.json()
            print(f"   Univers: {data.get('universe')}")
            print(f"   Total chips: {data.get('total_chips')}")
        else:
            print(f"❌ Endpoint Katula erreur: {response.status_code}")
            
        # Test endpoint Sessions
        response = requests.get("http://localhost:8000/api/session/sessions", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint Sessions accessible")
            data = response.json()
            print(f"   Total sessions: {data.get('total', 0)}")
        else:
            print(f"❌ Endpoint Sessions erreur: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend non accessible - Démarrez le backend avec:")
        print("   cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_backend()