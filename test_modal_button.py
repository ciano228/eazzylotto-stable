#!/usr/bin/env python3
"""
Test rapide du bouton modal
"""
import requests
import json

def test_session_creation():
    url = "http://localhost:8881/api/unified/session"
    
    test_data = {
        "name": "Test Modal Session",
        "description": "Test du bouton modal",
        "lottery_type": "Loto Test",
        "numbers_per_draw": 6,
        "total_draws": 10,
        "number_range_min": 1,
        "number_range_max": 90,
        "start_date": "01/01/2025",
        "lottery_schedule": [
            {"name": "Loto Test", "day_offset": 0}
        ],
        "cycle_length": 7
    }
    
    print(f"[TEST] POST {url}")
    print(f"[DATA] {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"[RESPONSE] Status: {response.status_code}")
        print(f"[RESPONSE] Body: {response.text}")
        
        if response.status_code == 200:
            print("[SUCCESS] Session créée!")
        else:
            print(f"[ERROR] Échec: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    test_session_creation()