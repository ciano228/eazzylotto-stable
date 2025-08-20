import requests

BASE_URL = "http://localhost:8000"

def test_login():
    """Test de connexion avec les identifiants existants"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Token: {data.get('access_token', 'N/A')[:30]}...")
        print(f"User ID: {data.get('user_id')}")
        return data.get('access_token')
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    print("Test de connexion")
    print("=" * 20)
    token = test_login()
    
    if token:
        print("\n[SUCCESS] Authentification complète fonctionnelle!")
    else:
        print("\n[ERROR] Problème de connexion")