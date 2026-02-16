#!/usr/bin/env python3
import requests
import json

# Test de sauvegarde d'un tirage
API_BASE = 'http://localhost:8881/api/unified'

# Données de test
session_id = 1  # Session "rodokpe lotories"
draw_number = 1
draw_data = {
    "numbers": [12, 34, 56, 78, 90],
    "draw_date": "2025-01-01",
    "lottery_name": "Test Loto",
    "is_no_draw": False
}

try:
    print(f"Test sauvegarde tirage #{draw_number} pour session {session_id}")
    print(f"Données: {draw_data}")
    
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/draws/{draw_number}",
        json=draw_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Statut: {response.status_code}")
    print(f"Réponse: {response.text}")
    
    if response.status_code == 200:
        print("✅ Sauvegarde réussie!")
        
        # Vérifier en base
        import psycopg2
        conn = psycopg2.connect(
            host='localhost', database='katooling_main_system',
            user='postgres', password='Katulaa_33', port=5432
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM session_draws WHERE session_id = %s", (session_id,))
        count = cursor.fetchone()[0]
        print(f"Tirages en base pour session {session_id}: {count}")
        
        cursor.close()
        conn.close()
    else:
        print("❌ Erreur sauvegarde")
        
except Exception as e:
    print(f"Erreur: {e}")