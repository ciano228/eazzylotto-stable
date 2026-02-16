#!/usr/bin/env python3
"""
Test du système smart-input avec sessions réelles
"""
import requests
import json
import time

API_BASE = "http://localhost:8881/api/unified"

def test_api_endpoints():
    print("[TEST] Vérification des endpoints API...")
    
    # Test 1: Liste des sessions
    try:
        response = requests.get(f"{API_BASE}/session/sessions")
        print(f"[OK] Sessions endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Sessions trouvées: {len(data.get('sessions', []))}")
    except Exception as e:
        print(f"[ERROR] Sessions endpoint: {e}")
    
    # Test 2: Création d'une session test
    session_data = {
        "name": "Test Session Auto",
        "description": "Session créée automatiquement pour test",
        "lottery_type": "Loto Test",
        "numbers_per_draw": 6,
        "total_draws": 21,
        "number_range_min": 1,
        "number_range_max": 90,
        "start_date": "01/01/2025",
        "lottery_schedule": [
            {"name": "Loto Mercredi", "day_offset": 2},
            {"name": "Loto Samedi", "day_offset": 5}
        ],
        "cycle_length": 7
    }
    
    try:
        response = requests.post(f"{API_BASE}/session", json=session_data)
        print(f"[OK] Création session: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Session créée: ID {result.get('session_id')}")
            return result.get('session_id')
    except Exception as e:
        print(f"[ERROR] Création session: {e}")
    
    return None

def test_session_activation(session_id):
    if not session_id:
        return
    
    try:
        response = requests.post(f"{API_BASE}/sessions/{session_id}/activate")
        print(f"[OK] Activation session: {response.status_code}")
        if response.status_code == 200:
            print(f"   Session {session_id} activée")
    except Exception as e:
        print(f"[ERROR] Activation session: {e}")

def main():
    print("=== TEST SMART INPUT SYSTEM ===")
    print(f"API Base: {API_BASE}")
    
    # Attendre que le serveur soit prêt
    print("\n[INFO] Attente du serveur...")
    time.sleep(2)
    
    # Tester les endpoints
    session_id = test_api_endpoints()
    
    # Tester l'activation
    test_session_activation(session_id)
    
    print("\n[SUCCESS] Tests terminés!")
    print("Vous pouvez maintenant ouvrir smart-input.html")

if __name__ == "__main__":
    main()