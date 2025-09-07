#!/usr/bin/env python3
"""
Test simple et rapide de l'endpoint temporel
"""
import requests

def test_simple():
    print("🔧 Test simple endpoint temporel...")
    
    try:
        # Test direct de l'endpoint temporal-periods
        url = "http://localhost:8000/api/analytics/temporal-periods/fruity"
        print(f"📞 Appel: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📅 Données disponibles: {data.get('available', False)}")
            if data.get('available'):
                print(f"   Période: {data.get('earliest_date')} → {data.get('latest_date')}")
                print(f"   Records: {data.get('total_records', 0)}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_simple()