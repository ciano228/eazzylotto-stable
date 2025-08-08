#!/usr/bin/env python3

import sys
sys.path.append('.')
from app.database.connection import get_db
from app.services.combination_service import CombinationService

def test_road1():
    db = next(get_db())
    
    print('=== TEST ROAD 1 FRUITY ===')
    
    # Test direct avec le service
    combinations = CombinationService.get_combinations_by_denomination(
        db, "road 1", "fruity"
    )
    
    print(f"Résultats trouvés: {len(combinations)}")
    
    for combo in combinations:
        print(f"- {combo['combination']} | Position: {combo['alpha_ranking']} | Dénomination: {combo['denomination']}")
    
    # Test API
    print('\n=== TEST API ROAD 1 ===')
    import requests
    
    try:
        url = "http://localhost:8006/api/analytics/denomination/fruity/road%201"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API - {data.get('total_occurrences', 0)} occurrences")
            
            for detail in data.get('details', [])[:3]:
                print(f"- {detail.get('combination')} | Position: {detail.get('alpha_ranking')}")
        else:
            print(f"Erreur: {response.text}")
            
    except Exception as e:
        print(f"Erreur API: {e}")

if __name__ == "__main__":
    test_road1()