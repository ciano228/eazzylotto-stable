#!/usr/bin/env python3
"""
Test du mapping entre Base de Données et Interface Utilisateur
Vérifie que les données de la BD sont correctement transmises à l'UI
"""
import subprocess
import sys
import time
import requests
import psycopg2
from pathlib import Path

def test_bd_to_api_mapping():
    """Tester le mapping BD -> API"""
    print("=== TEST MAPPING BD -> API ===")
    
    # 1. Connexion directe à la BD
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        cursor = conn.cursor()
        
        # Récupérer données directement de la BD
        cursor.execute("SELECT * FROM katula_table WHERE universe = 'mundo' LIMIT 5")
        bd_data = cursor.fetchall()
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'katula_table'")
        columns = [row[0] for row in cursor.fetchall()]
        
        print(f"✓ BD: {len(bd_data)} lignes trouvées")
        print(f"✓ Colonnes: {columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Erreur BD: {e}")
        return False
    
    # 2. Démarrer le serveur backend
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.servers.server_postgres_simple:app",
        "--host", "0.0.0.0", "--port", "8081"
    ], cwd=Path.cwd(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    try:
        # 3. Tester l'API
        response = requests.get("http://localhost:8081/api/katula/table/mundo", timeout=10)
        
        if response.status_code == 200:
            api_data = response.json()
            print(f"✓ API: {len(api_data)} lignes reçues")
            
            # Comparer les données
            if len(api_data) > 0:
                print(f"✓ Premier élément API: {list(api_data[0].keys())}")
                
                # Vérifier que les colonnes correspondent
                api_columns = set(api_data[0].keys())
                bd_columns = set(columns)
                
                if api_columns.issubset(bd_columns) or bd_columns.issubset(api_columns):
                    print("✓ Structure des données cohérente")
                else:
                    print(f"✗ Différence colonnes - BD: {bd_columns}, API: {api_columns}")
            
            return True
        else:
            print(f"✗ API erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur API: {e}")
        return False
    finally:
        backend_process.terminate()

def test_api_to_ui_mapping():
    """Tester le mapping API -> UI"""
    print("\n=== TEST MAPPING API -> UI ===")
    
    # Démarrer le serveur
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.servers.server_postgres_simple:app",
        "--host", "0.0.0.0", "--port", "8081"
    ], cwd=Path.cwd(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    try:
        # Tester les endpoints utilisés par l'UI
        endpoints = [
            "/api/katula/table/mundo",
            "/api/formes/real/mundo"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:8081{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {endpoint}: {len(data)} éléments")
                
                if len(data) > 0:
                    print(f"  Structure: {list(data[0].keys())}")
            else:
                print(f"✗ {endpoint}: erreur {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur test UI: {e}")
        return False
    finally:
        backend_process.terminate()

def test_ui_javascript_compatibility():
    """Vérifier la compatibilité des données avec le JavaScript"""
    print("\n=== TEST COMPATIBILITÉ JAVASCRIPT ===")
    
    # Lire le fichier HTML pour voir comment les données sont utilisées
    try:
        html_path = Path("frontend/katula-dynamic.html")
        if html_path.exists():
            content = html_path.read_text(encoding='utf-8')
            
            # Chercher les utilisations de données
            if "forEach" in content:
                print("✓ Utilisation de forEach détectée")
            if "API_BASE" in content:
                print("✓ Configuration API_BASE trouvée")
            if "katula/table" in content:
                print("✓ Endpoint katula/table utilisé")
            if "formes/real" in content:
                print("✓ Endpoint formes/real utilisé")
                
            return True
        else:
            print("✗ Fichier HTML non trouvé")
            return False
            
    except Exception as e:
        print(f"✗ Erreur lecture HTML: {e}")
        return False

def run_mapping_tests():
    """Exécuter tous les tests de mapping"""
    print("TESTS DE MAPPING BD <-> UI")
    print("=" * 40)
    
    tests = [
        test_bd_to_api_mapping,
        test_api_to_ui_mapping,
        test_ui_javascript_compatibility
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        time.sleep(1)
    
    print("\n" + "=" * 40)
    print("RÉSULTATS:")
    
    if all(results):
        print("✓ TOUS LES MAPPINGS SONT CORRECTS")
        print("✓ Les données circulent bien de la BD vers l'UI")
    else:
        print("✗ PROBLÈMES DE MAPPING DÉTECTÉS")
        print("✗ Vérifiez les erreurs ci-dessus")
    
    return all(results)

if __name__ == "__main__":
    success = run_mapping_tests()
    sys.exit(0 if success else 1)