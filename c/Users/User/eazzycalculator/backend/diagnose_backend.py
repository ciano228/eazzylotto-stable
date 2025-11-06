#!/usr/bin/env python3
"""
Script de diagnostic pour le backend EazzyLotto
Identifie les problèmes de démarrage du serveur
"""

import os
import sys
import subprocess
import socket
import psycopg2
from dotenv import load_dotenv
import importlib.util

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print('='*50)

def print_status(message, status):
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def check_python_version():
    print_header("VÉRIFICATION PYTHON")
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print_status("Version Python compatible", True)
        return True
    else:
        print_status("Version Python trop ancienne (requis: 3.8+)", False)
        return False

def check_port_availability(port):
    print_header(f"VÉRIFICATION PORT {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print_status(f"Port {port} est OCCUPÉ", False)
            return False
        else:
            print_status(f"Port {port} est LIBRE", True)
            return True
    finally:
        sock.close()

def check_dependencies():
    print_header("VÉRIFICATION DÉPENDANCES")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'python-dotenv',
        'pandas',
        'numpy'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package.replace('-', '_'))
            if spec is not None:
                print_status(f"{package} installé", True)
            else:
                print_status(f"{package} MANQUANT", False)
                all_good = False
        except ImportError:
            print_status(f"{package} MANQUANT", False)
            all_good = False
    
    return all_good

def check_env_file():
    print_header("VÉRIFICATION FICHIER .env")
    
    if not os.path.exists('.env'):
        print_status("Fichier .env MANQUANT", False)
        return False
    
    load_dotenv()
    
    required_vars = ['DATABASE_URL']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print_status(f"{var} configuré", True)
        else:
            print_status(f"{var} MANQUANT", False)
            all_good = False
    
    return all_good

def check_database_connection():
    print_header("VÉRIFICATION BASE DE DONNÉES")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print_status("DATABASE_URL non configuré", False)
        return False
    
    try:
        # Extraire les infos de connexion
        # Format: postgresql://user:password@host:port/database
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
        
        if not match:
            print_status("Format DATABASE_URL invalide", False)
            return False
        
        user, password, host, port, database = match.groups()
        
        print(f"Tentative de connexion à:")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Database: {database}")
        print(f"  User: {user}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print_status(f"Connexion PostgreSQL réussie", True)
        print(f"Version PostgreSQL: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_status(f"Erreur connexion base de données: {str(e)}", False)
        return False

def check_fastapi_app():
    print_header("VÉRIFICATION APPLICATION FASTAPI")
    
    try:
        # Essayer d'importer l'application
        sys.path.append('.')
        from main import app
        print_status("Application FastAPI importée avec succès", True)
        
        # Vérifier les routes
        routes = [route.path for route in app.routes]
        print(f"Routes disponibles: {len(routes)}")
        for route in routes[:5]:  # Afficher les 5 premières
            print(f"  - {route}")
        
        return True
        
    except Exception as e:
        print_status(f"Erreur import FastAPI: {str(e)}", False)
        return False

def suggest_fixes():
    print_header("SUGGESTIONS DE CORRECTION")
    
    print("🔧 Pour corriger les problèmes identifiés:")
    print()
    print("1. DÉPENDANCES MANQUANTES:")
    print("   pip install -r requirements.txt")
    print()
    print("2. POSTGRESQL NON DÉMARRÉ:")
    print("   - Windows: Services → PostgreSQL → Démarrer")
    print("   - Linux: sudo systemctl start postgresql")
    print()
    print("3. PORT OCCUPÉ:")
    print("   - Windows: netstat -ano | findstr :8000")
    print("   - Tuer le processus ou changer de port")
    print()
    print("4. FICHIER .env MANQUANT:")
    print("   - Copier .env.example vers .env")
    print("   - Configurer DATABASE_URL")
    print()
    print("5. DÉMARRAGE BACKEND:")
    print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

def main():
    print("🚀 DIAGNOSTIC BACKEND EAZZYLOTTO")
    print("=" * 50)
    
    # Changer vers le répertoire backend
    if os.path.basename(os.getcwd()) != 'backend':
        if os.path.exists('backend'):
            os.chdir('backend')
            print("📁 Changement vers le dossier backend")
        else:
            print("❌ Dossier backend non trouvé")
            return
    
    results = []
    
    # Tests de diagnostic
    results.append(("Python", check_python_version()))
    results.append(("Port 8000", check_port_availability(8000)))
    results.append(("Dépendances", check_dependencies()))
    results.append(("Fichier .env", check_env_file()))
    results.append(("Base de données", check_database_connection()))
    results.append(("Application FastAPI", check_fastapi_app()))
    
    # Résumé
    print_header("RÉSUMÉ DU DIAGNOSTIC")
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    print()
    
    for test_name, status in results:
        print_status(f"{test_name}", status)
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés !")
        print("Votre backend devrait pouvoir démarrer normalement.")
        print("\nPour démarrer:")
        print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print(f"\n⚠️ {total - passed} problème(s) détecté(s)")
        suggest_fixes()

if __name__ == "__main__":
    main()
