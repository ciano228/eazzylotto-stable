#!/usr/bin/env python3

import requests
import json

def test_api_direct():
    base_url = "http://localhost:8006/api/analytics"
    
    print('=== TEST API DIRECT ===')
    
    # Test avec une dénomination simple qui fonctionne
    test_cases = [
        "star 3",
        "bed 1", 
        "drum 9"
    ]
    
    for denomination in test_cases:
        print(f'\n🔍 Test: "{denomination}" dans fruity')
        
        try:
            from urllib.parse import quote
            encoded_denomination = quote(denomination)
            url = f"{base_url}/denomination/fruity/{encoded_denomination}"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Succès - {data.get('total_occurrences', 0)} occurrences")
                
                details = data.get('details', [])
                for i, detail in enumerate(details[:2]):
                    print(f"  {i+1}. {detail.get('denomination', 'N/A')} | {detail.get('combination', 'N/A')} | Position: {detail.get('alpha_ranking', 'N/A')}")
                    
            elif response.status_code == 404:
                print(f"❌ 404 - Endpoint ou dénomination non trouvée")
                print(f"Réponse: {response.text}")
            else:
                print(f"❌ Erreur {response.status_code}")
                print(f"Réponse: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erreur de connexion - Le backend n'est pas démarré")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_api_direct()