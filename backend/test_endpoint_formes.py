#!/usr/bin/env python3
"""
Test direct de l'endpoint formes
"""
import requests
import json

def test_formes_endpoint():
    """Test direct de l'endpoint formes"""
    base_url = "http://localhost:8006/api/analytics/formes"
    universes = ["mundo", "fruity", "trigga", "roaster", "sunshine"]
    
    for universe in universes:
        try:
            print(f"\n🌍 TEST UNIVERS: {universe.upper()}")
            print("=" * 50)
            
            url = f"{base_url}/{universe}"
            response = requests.get(url)
            
            print(f"📡 URL: {url}")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"🎨 Formes: {data.get('formes', [])}")
                print(f"📈 Total: {data.get('total_formes', 0)}")
                print(f"🔧 Géométrie variable: {data.get('is_variable_geometry', False)}")
                
                if 'error' in data:
                    print(f"❌ Erreur: {data['error']}")
            else:
                print(f"❌ Erreur HTTP: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_formes_endpoint()