#!/usr/bin/env python3
"""
Test rapide pour vérifier la correction de la dénomination 'table 2'
"""
import requests
import urllib.parse

def test_denomination_api():
    base_url = "http://localhost:8881"
    universe = "mundo"
    denomination = "table 2"
    
    # Test avec encodage URL
    encoded_denom = urllib.parse.quote(denomination)
    url = f"{base_url}/api/denomination/{universe}/{encoded_denom}"
    
    print(f"Test URL: {url}")
    print(f"Dénomination originale: '{denomination}'")
    print(f"Dénomination encodée: '{encoded_denom}'")
    
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Réponse: {data}")
            
            if data.get('status') == 'success':
                print(f"✅ Succès! {data.get('total_combinations', 0)} combinations trouvées")
                return True
            else:
                print(f"❌ Erreur API: {data.get('error', 'Inconnue')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    print("=== TEST CORRECTION DÉNOMINATION ===")
    success = test_denomination_api()
    print(f"Résultat: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")