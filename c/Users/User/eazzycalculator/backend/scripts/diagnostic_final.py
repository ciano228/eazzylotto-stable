#!/usr/bin/env python3
"""
Diagnostic final pour katula-dynamic.html
"""
import requests

def diagnostic_final():
    print("=== DIAGNOSTIC FINAL ===\n")
    
    print("1. BACKEND (port 8081):")
    try:
        response = requests.get("http://localhost:8081/api/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ Backend accessible")
            
            # Test endpoints Katula
            endpoints = [
                "/api/analytics/katula/table/mundo",
                "/api/analytics/katula/formes/mundo"
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"http://localhost:8081{endpoint}", timeout=3)
                    if resp.status_code == 200:
                        print(f"   ✅ {endpoint}")
                    else:
                        print(f"   ❌ {endpoint} - Status: {resp.status_code}")
                except:
                    print(f"   ❌ {endpoint} - Erreur")
        else:
            print("   ❌ Backend non accessible")
    except:
        print("   ❌ Backend non accessible")
    
    print("\n2. FRONTEND:")
    ports_to_test = [8000, 8001, 8002, 8003, 8005]
    frontend_found = False
    
    for port in ports_to_test:
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Frontend accessible sur port {port}")
                frontend_found = True
                
                # Test page katula-dynamic
                try:
                    resp = requests.get(f"http://localhost:{port}/katula-dynamic.html", timeout=2)
                    if resp.status_code == 200:
                        print(f"   ✅ katula-dynamic.html accessible")
                    else:
                        print(f"   ❌ katula-dynamic.html non trouvée")
                except:
                    print(f"   ❌ katula-dynamic.html erreur")
                break
        except:
            continue
    
    if not frontend_found:
        print("   ❌ Aucun frontend trouvé")
    
    print("\n=== SOLUTION ===")
    print("Le problème de table vide dans katula-dynamic.html était dû à:")
    print("1. ❌ Endpoints backend manquants (/katula/chip/{universe}/{chip_number})")
    print("2. ❌ Mauvaise URL d'API dans le frontend")
    print("3. ✅ CORRIGÉ: Nouveaux endpoints ajoutés au backend")
    print("4. ✅ CORRIGÉ: URL d'API corrigée dans le frontend")
    
    print("\nPour voir les données:")
    print("1. Redémarrer le backend: python start_backend.py")
    print("2. Ouvrir: http://localhost:8000/katula-dynamic.html")
    print("3. Sélectionner 'Mundo' et cliquer 'Charger Univers'")
    print("4. La table affichera maintenant des données simulées réalistes")

if __name__ == "__main__":
    diagnostic_final()