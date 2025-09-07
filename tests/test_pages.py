#!/usr/bin/env python3
"""
Script de test pour vérifier les erreurs de chargement des pages
"""
import requests
import json

def test_backend():
    """Tester les endpoints du backend"""
    print("=== TEST BACKEND ===")
    
    endpoints = [
        "http://localhost:8081/api/health",
        "http://localhost:8081/api/analytics/katula/formes/mundo",
        "http://localhost:8081/api/analytics/katula/table/mundo"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {endpoint}")
                data = response.json()
                if 'formes' in data:
                    print(f"   Formes: {data['formes']}")
                elif 'total_chips' in data:
                    print(f"   Chips: {data['total_chips']}")
            else:
                print(f"[ERROR] {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {endpoint} - Erreur: {e}")
    
    print()

def test_frontend():
    """Tester l'accès au frontend"""
    print("=== TEST FRONTEND ===")
    
    # Essayer différents ports
    ports = [8000, 8001, 8002, 8003, 8005]
    
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Frontend accessible sur port {port}")
                return port
            else:
                print(f"[ERROR] Port {port} - Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Port {port} - Erreur: {e}")
    
    print("[ERROR] Aucun frontend accessible")
    return None

if __name__ == "__main__":
    print("[DIAGNOSTIC] ERREURS DE CHARGEMENT\n")
    
    # Test backend
    test_backend()
    
    # Test frontend
    frontend_port = test_frontend()
    
    print("\n=== RESUME ===")
    print("[OK] Backend: http://localhost:8081 (FONCTIONNEL)")
    if frontend_port:
        print(f"[OK] Frontend: http://localhost:{frontend_port}")
        print(f"[PAGE] Katula: http://localhost:{frontend_port}/katula-forme-layout.html")
    else:
        print("[ERROR] Frontend: NON ACCESSIBLE")
        print("[SOLUTION] Demarrer le frontend avec 'python start_frontend.py'")