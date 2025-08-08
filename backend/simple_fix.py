#!/usr/bin/env python3
"""
Script de correction simple pour le backend EazzyLotto
"""

import os
import sys
import subprocess
import socket
import time
import psutil

def print_header(title):
    print(f"\n{'='*50}")
    print(f"[FIX] {title}")
    print('='*50)

def print_status(message, status):
    icon = "[OK]" if status else "[ERROR]"
    print(f"{icon} {message}")

def kill_process_on_port(port):
    """Tue tous les processus utilisant le port"""
    print_header(f"LIBERATION DU PORT {port}")
    
    killed_any = False
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections'] or []:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        print(f"Processus trouve: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
                        killed_any = True
                        print_status(f"Processus {proc.info['pid']} termine", True)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print_status(f"Erreur liberation port: {e}", False)
    
    if not killed_any:
        print_status("Aucun processus trouve sur ce port", True)
    
    time.sleep(2)
    return check_port_free(port)

def check_port_free(port):
    """Verifie si un port est libre"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('localhost', port))
        return result != 0
    finally:
        sock.close()

def install_dependencies():
    """Installe les dependances"""
    print_header("INSTALLATION DES DEPENDANCES")
    
    # Packages critiques
    critical_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2-binary',
        'python-dotenv',
        'pydantic',
        'python-multipart'
    ]
    
    all_success = True
    for package in critical_packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True, check=True)
            print_status(f"{package} installe", True)
        except subprocess.CalledProcessError:
            print_status(f"Erreur installation {package}", False)
            all_success = False
    
    return all_success

def fix_main_py():
    """Corrige main.py"""
    print_header("CORRECTION DE MAIN.PY")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixes_applied = []
        
        # Corriger les chemins des assets
        if '../../frontend/assets' in content:
            content = content.replace('../../frontend/assets', '../frontend/assets')
            content = content.replace('../../frontend', '../frontend')
            fixes_applied.append("Chemins assets corriges")
        
        # Ajouter endpoint de sante
        if '/api/health' not in content:
            health_endpoint = '''
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Backend EazzyLotto operationnel"}
'''
            content = content.rstrip() + health_endpoint + '\n'
            fixes_applied.append("Endpoint de sante ajoute")
        
        if fixes_applied:
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            for fix in fixes_applied:
                print_status(fix, True)
        else:
            print_status("Aucune correction necessaire", True)
        
        return True
        
    except Exception as e:
        print_status(f"Erreur correction main.py: {e}", False)
        return False

def start_backend():
    """Demarre le backend"""
    print_header("DEMARRAGE DU BACKEND")
    
    try:
        cmd = [
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--reload', '--host', '0.0.0.0', '--port', '8000'
        ]
        
        print("Demarrage du serveur FastAPI...")
        print(f"Commande: {' '.join(cmd)}")
        
        # Demarrer le processus
        process = subprocess.Popen(cmd)
        
        # Attendre un peu
        time.sleep(5)
        
        # Verifier si le port est maintenant occupe (bon signe)
        if not check_port_free(8000):
            print_status("Backend demarre avec succes", True)
            print("Backend accessible sur: http://localhost:8000")
            print("Documentation API: http://localhost:8000/docs")
            return True
        else:
            print_status("Erreur demarrage backend", False)
            return False
            
    except Exception as e:
        print_status(f"Erreur demarrage: {e}", False)
        return False

def main():
    print("CORRECTION AUTOMATIQUE BACKEND EAZZYLOTTO")
    print("=" * 50)
    
    # Aller dans le bon repertoire
    if os.path.basename(os.getcwd()) != 'backend':
        if os.path.exists('backend'):
            os.chdir('backend')
            print("Changement vers le dossier backend")
        else:
            print("Dossier backend non trouve")
            return False
    
    success_count = 0
    total_steps = 4
    
    # Etape 1: Liberer le port
    if kill_process_on_port(8000):
        success_count += 1
    
    # Etape 2: Installer dependances
    if install_dependencies():
        success_count += 1
    
    # Etape 3: Corriger main.py
    if fix_main_py():
        success_count += 1
    
    # Etape 4: Demarrer backend
    if start_backend():
        success_count += 1
    
    # Resultat final
    print_header("RESUME FINAL")
    print(f"Etapes reussies: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("\nSUCCES COMPLET!")
        print("Tous les problemes ont ete resolus")
        print("Backend demarre et fonctionnel")
        print("\nLIENS UTILES:")
        print("- Backend: http://localhost:8000")
        print("- API Docs: http://localhost:8000/docs")
        print("- Sessions: http://localhost:8000/api/session/sessions")
        print("\nVotre plateforme EazzyLotto est maintenant operationnelle!")
    else:
        print(f"\n{total_steps - success_count} probleme(s) restant(s)")
    
    return success_count == total_steps

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")
    except Exception as e:
        print(f"\nErreur inattendue: {e}")
