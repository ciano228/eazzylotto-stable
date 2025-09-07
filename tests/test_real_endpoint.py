#!/usr/bin/env python3
"""
Tester l'endpoint réel avec les vraies données
"""
import requests

def test_real_endpoint():
    print("Test de l'endpoint réel avec vraies données PostgreSQL...")
    
    try:
        # Test endpoint Katula avec vraies données
        response = requests.get("http://localhost:8000/api/analytics/katula/table/mundo", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint accessible")
            print(f"   Source: {data.get('data_source', 'unknown')}")
            print(f"   Univers: {data.get('universe')}")
            print(f"   Total chips: {data.get('total_chips')}")
            
            # Vérifier la structure
            if 'statistics' in data:
                stats = data['statistics']
                print(f"   Entrées totales: {stats.get('total_entries')}")
                print(f"   Positions uniques: {stats.get('unique_positions')}")
                print(f"   Formes: {stats.get('total_formes')}")
                print(f"   Score complexité: {stats.get('complexity_score', 0):.2f}")
            
            # Vérifier quelques positions
            if 'chip_positions' in data:
                positions = list(data['chip_positions'].items())[:3]
                print("   Exemples positions:")
                for chip_id, info in positions:
                    formes = info.get('formes', {})
                    print(f"     {chip_id}: {len(formes)} formes - {list(formes.keys())}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend non accessible")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_real_endpoint()