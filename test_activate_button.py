#!/usr/bin/env python3
"""
Test du bouton Activer
"""
import requests

def test_activate_session():
    # D'abord lister les sessions
    print("[1] Liste des sessions...")
    response = requests.get("http://localhost:8881/api/unified/session/sessions")
    if response.status_code == 200:
        sessions = response.json()['sessions']
        print(f"   Sessions trouvées: {len(sessions)}")
        
        if sessions:
            # Prendre la première session
            session_id = sessions[0]['id']
            print(f"   Test avec session ID: {session_id}")
            
            # Tester l'activation
            print(f"[2] Activation session {session_id}...")
            activate_response = requests.post(f"http://localhost:8881/api/unified/sessions/{session_id}/activate")
            print(f"   Status: {activate_response.status_code}")
            print(f"   Response: {activate_response.text}")
            
            if activate_response.status_code == 200:
                print("[SUCCESS] Session activée!")
            else:
                print(f"[ERROR] Échec activation: {activate_response.status_code}")
        else:
            print("[ERROR] Aucune session disponible")
    else:
        print(f"[ERROR] Impossible de lister les sessions: {response.status_code}")

if __name__ == "__main__":
    test_activate_session()