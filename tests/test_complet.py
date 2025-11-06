#!/usr/bin/env python3
"""
Script de test complet pour EazzyCalculator
Vérifie tous les composants principaux
"""
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def print_status(message, status="INFO"):
    """Afficher un message avec statut"""
    print(f"{status}: {message}")

def test_database_connection():
    """Tester la connexion à PostgreSQL"""
    print_status("Test de connexion PostgreSQL...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            database='katooling_main_system',
            user='postgres',
            password='Katulaa_33',
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        conn.close()
        
        print_status(f"PostgreSQL connecté - {len(tables)} tables trouvées", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Erreur PostgreSQL: {e}", "ERROR")
        return False

def test_backend_server():
    """Tester le serveur backend"""
    print_status("Test du serveur backend...")
    
    try:
        # Démarrer le serveur en arrière-plan
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.servers.server_postgres_simple:app",
            "--host", "0.0.0.0", "--port", "8081"
        ], cwd=Path.cwd())
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        # Tester l'endpoint health
        response = requests.get("http://localhost:8081/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Backend OK - Status: {data.get('status')}", "SUCCESS")
            backend_process.terminate()
            return True
        else:
            print_status(f"Backend erreur: {response.status_code}", "ERROR")
            backend_process.terminate()
            return False
            
    except Exception as e:
        print_status(f"Erreur backend: {e}", "ERROR")
        try:
            backend_process.terminate()
        except:
            pass
        return False

def test_frontend_files():
    """Vérifier les fichiers frontend"""
    print_status("Vérification des fichiers frontend...")
    
    required_files = [
        "frontend/katula-dynamic.html",
        "frontend/assets/js/universal-header.js",
        "frontend/assets/css/eazzylotto-icons.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"Fichiers manquants: {missing_files}", "ERROR")
        return False
    else:
        print_status("Tous les fichiers frontend présents", "SUCCESS")
        return True

def test_api_endpoints():
    """Tester les endpoints API principaux"""
    print_status("Test des endpoints API...")
    
    # Démarrer le serveur temporairement
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.servers.server_postgres_simple:app",
        "--host", "0.0.0.0", "--port", "8081"
    ], cwd=Path.cwd(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    endpoints_to_test = [
        "/api/health",
        "/api/katula/table/mundo",
        "/api/katula/formes/mundo"
    ]
    
    results = []
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"http://localhost:8081{endpoint}", timeout=5)
            if response.status_code == 200:
                print_status(f"OK {endpoint}", "SUCCESS")
                results.append(True)
            else:
                print_status(f"FAIL {endpoint} - {response.status_code}", "ERROR")
                results.append(False)
        except Exception as e:
            print_status(f"FAIL {endpoint} - {e}", "ERROR")
            results.append(False)
    
    backend_process.terminate()
    return all(results)

def run_complete_test():
    """Exécuter tous les tests"""
    print_status("=== DÉBUT DES TESTS COMPLETS ===")
    print_status(f"Répertoire de travail: {Path.cwd()}")
    
    tests = [
        ("Base de données", test_database_connection),
        ("Fichiers frontend", test_frontend_files),
        ("Serveur backend", test_backend_server),
        ("Endpoints API", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print_status(f"\n--- Test: {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    print_status("\n=== RÉSULTATS FINAUX ===")
    all_passed = True
    for test_name, result in results:
        status = "SUCCESS" if result else "ERROR"
        symbol = "OK" if result else "FAIL"
        print_status(f"{symbol} {test_name}", status)
        if not result:
            all_passed = False
    
    if all_passed:
        print_status("\nTOUS LES TESTS SONT PASSES!", "SUCCESS")
        print_status("L'application est prête à être utilisée!", "SUCCESS")
        print_status("\nPour démarrer l'application:", "INFO")
        print_status("1. Backend: python -m uvicorn backend.servers.server_postgres_simple:app --host 0.0.0.0 --port 8081", "INFO")
        print_status("2. Frontend: Ouvrir frontend/katula-dynamic.html dans un navigateur", "INFO")
    else:
        print_status("\nCERTAINS TESTS ONT ECHOUE", "ERROR")
        print_status("Vérifiez les erreurs ci-dessus avant de continuer", "WARNING")
    
    return all_passed

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)