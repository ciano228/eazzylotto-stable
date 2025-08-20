import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test de l'endpoint de santé"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"[OK] Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

def test_register():
    """Test d'inscription"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"[OK] Register: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   User ID: {data.get('user_id')}")
            return data.get('access_token')
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Register failed: {e}")
        return None

def test_login():
    """Test de connexion"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"[OK] Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   User ID: {data.get('user_id')}")
            return data.get('access_token')
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test d'un endpoint protégé"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/session/test", headers=headers)
        print(f"[OK] Protected endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Protected endpoint failed: {e}")

if __name__ == "__main__":
    print("Test de l'authentification EazzyCalculator")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("[ERROR] Serveur non disponible")
        exit(1)
    
    print()
    
    # Test 2: Inscription
    token = test_register()
    if not token:
        print("[WARNING] Inscription echouee, test de connexion...")
        token = test_login()
    
    print()
    
    # Test 3: Connexion (si inscription a échoué)
    if not token:
        token = test_login()
    
    print()
    
    # Test 4: Endpoint protégé
    if token:
        test_protected_endpoint(token)
    else:
        print("[ERROR] Aucun token disponible pour tester les endpoints proteges")
    
    print()
    print("[INFO] Tests termines")