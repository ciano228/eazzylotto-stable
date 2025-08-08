#!/usr/bin/env python3

import sys
sys.path.append('.')
import requests
import json

def test_api_denomination():
    base_url = "http://localhost:8006/api/analytics"
    
    print('=== TEST API DÉNOMINATION MULTIPLE ===')
    
    # Test avec dénomination multiple
    test_cases = [
        ("star 3/star 7", "fruity"),
        ("bed 1/bed 8", "fruity"),
        ("star 3", "fruity"),  # Test simple
    ]
    
    for denomination, universe in test_cases:
        print(f"\n🔍 Test: '{denomination}' dans {universe}")
        
        try:
            # Encoder correctement l'URL
            from urllib.parse import quote
            encoded_denomination = quote(denomination)
            url = f"{base_url}/denomination/{universe}/{encoded_denomination}"
            print(f"URL: {url}")
            
            response = requests.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Succès - {data.get('total_occurrences', 0)} occurrences")
                
                # Afficher les détails
                details = data.get('details', [])
                for i, detail in enumerate(details[:3]):  # Limiter à 3 pour la lisibilité
                    print(f"  {i+1}. {detail.get('denomination', 'N/A')} | {detail.get('combination', 'N/A')} | Position: {detail.get('alpha_ranking', 'N/A')}")
                
                if len(details) > 3:
                    print(f"  ... et {len(details) - 3} autres")
                    
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_api_denomination()