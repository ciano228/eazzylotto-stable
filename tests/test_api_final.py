#!/usr/bin/env python3
"""
Tests finaux pour l'API EazzyLotto
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test de santé de l'API"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ API Health: {e}")
        return False

def test_auth_endpoints():
    """Test des endpoints d'authentification"""
    # Test d'inscription
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    try:
        # Inscription
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        print(f"✓ Register: {response.status_code}")
        
        # Connexion
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        print(f"✓ Login: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✓ Token reçu: {token[:20]}...")
            return token
        
    except Exception as e:
        print(f"✗ Auth Error: {e}")
    
    return None

def test_protected_endpoints(token):
    """Test des endpoints protégés"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/protected", headers=headers)
        print(f"✓ Protected endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Protected endpoint: {e}")
        return False

def main():
    print("========================================")
    print("    TESTS API EAZZYLOTTO")
    print("========================================")
    
    # Test 1: Santé de l'API
    if not test_api_health():
        print("ERREUR: API non accessible")
        return
    
    # Test 2: Authentification
    token = test_auth_endpoints()
    if not token:
        print("ERREUR: Authentification échouée")
        return
    
    # Test 3: Endpoints protégés
    test_protected_endpoints(token)
    
    print("\n✓ Tous les tests API terminés")

if __name__ == "__main__":
    main()