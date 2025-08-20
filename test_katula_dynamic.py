#!/usr/bin/env python3
"""
Test de la page katula-dynamic.html avec données simulées
"""
import requests
import json

def test_katula_dynamic():
    print("[TEST] Vérification de katula-dynamic.html")
    
    # Test 1: Vérifier que la page se charge
    try:
        response = requests.get("http://localhost:8000/katula-dynamic.html", timeout=5)
        if response.status_code == 200:
            print("[OK] Page katula-dynamic.html accessible")
        else:
            print(f"[ERROR] Page non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Impossible d'accéder à la page: {e}")
        return False
    
    # Test 2: Vérifier les endpoints backend nécessaires
    endpoints_to_test = [
        "http://localhost:8081/api/analytics/katula/table/mundo",
        "http://localhost:8081/api/analytics/katula/formes/mundo"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {endpoint.split('/')[-1]} - {len(data)} clés")
            else:
                print(f"[ERROR] {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {endpoint} - Erreur: {e}")
    
    print("\n[SOLUTION] Pour corriger la table vide:")
    print("1. Redémarrer le backend pour charger les nouveaux endpoints")
    print("2. Ouvrir http://localhost:8000/katula-dynamic.html")
    print("3. Sélectionner 'Mundo' et cliquer 'Charger Univers'")
    print("4. La table devrait maintenant afficher des données simulées")
    
    return True

if __name__ == "__main__":
    test_katula_dynamic()