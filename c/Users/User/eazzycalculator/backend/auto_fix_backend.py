#!/usr/bin/env python3
"""
Script de correction automatique pour le backend EazzyLotto
Résout automatiquement tous les problèmes identifiés
"""

import os
import sys
import subprocess
import socket
import time
import signal
import psutil

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)

def print_status(message, status):
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def kill_process_on_port(port):
    """Tue tous les processus utilisant le port spécifié"""
    print_header(f"LIBÉRATION DU PORT {port}")
    
    killed_any = False
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info['connections'] or []:
                if conn.laddr.port == port:
                    print(f"🔫 Processus trouvé: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
                    killed_any = True
                    print_status(f"Processus {proc.info['pid']} terminé", True)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not killed_any:
        print_status("Aucun processus trouvé sur ce port", True)
    
    # Attendre que le port soit libéré
    time.sleep(2)
    return check_port_free(port)

def check_port_free(port):
    """Vérifie si un port est libre"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('localhost', port))
        return result != 0  # True si libre, False si occupé
    finally:
        sock.close()

def install_dependencies():
    """Installe toutes les dépendances requises"""
    print_header("INSTALLATION DES DÉPENDANCES")
    
    try:
        # Installer les dépendances depuis requirements.txt
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, check=True)
        
        print_status("Dépendances installées depuis requirements.txt", True)
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Erreur installation requirements.txt: {e}", False)
        
        # Installation manuelle des packages critiques
        critical_packages = [
            'fastapi==0.104.1',
            'uvicorn==0.24.0',
            'sqlalchemy==2.0.23',
            'psycopg2-binary==2.9.9',
            'python-dotenv==1.0.0',
            'pydantic==2.5.0',
            'python-multipart==0.0.6'
        ]
        
        print("📦 Installation manuelle des packages critiques...")
        all_success = True
        
        for package in critical_packages:
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                print_status(f"{package} installé", True)
            except subprocess.CalledProcessError:
                print_status(f"Erreur installation {package}", False)
                all_success = False
        
        return all_success

def fix_main_py():
    """Corrige les problèmes dans main.py"""
    print_header("CORRECTION DE MAIN.PY")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrections nécessaires
        fixes_applied = []
        
        # 1. Corriger les chemins des assets
        if '../../frontend/assets' in content:
            content = content.replace('../../frontend/assets', '../frontend/assets')
            content = content.replace('../../frontend', '../frontend')
            fixes_applied.append("Chemins assets corrigés")
        
        # 2. Ajouter un endpoint de santé si manquant
        if '/api/health' not in content:
            health_endpoint = '''
@app.get("/api/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy", "message": "Backend EazzyLotto opérationnel"}
'''
            # Ajouter avant la dernière ligne
            content = content.rstrip() + health_endpoint + '\n'
            fixes_applied.append("Endpoint de santé ajouté")
        
        # 3. Sauvegarder les corrections
        if fixes_applied:
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            for fix in fixes_applied:
                print_status(fix, True)
        else:
            print_status("Aucune correction nécessaire dans main.py", True)
        
        return True
        
    except Exception as e:
        print_status(f"Erreur correction main.py: {e}", False)
        return False

def start_backend():
    """Démarre le backend FastAPI"""
    print_header("DÉMARRAGE DU BACKEND")
    
    try:
        # Commande de démarrage
        cmd = [
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--reload', '--host', '0.0.0.0', '--port', '8000'
        ]
        
        print("🚀 Démarrage du serveur FastAPI...")
        print(f"Commande: {' '.join(cmd)}")
        
        # Démarrer en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour voir si ça démarre
        time.sleep(3)
        
        # Vérifier si le processus est toujours en vie
        if process.poll() is None:
            print_status("Backend démarré avec succès", True)
            print("📍 Backend accessible sur: http://localhost:8000")
            print("📚 Documentation API: http://localhost:8000/docs")
            print("🔍 Sessions API: http://localhost:8000/api/session/sessions")
            return True
        else:
            stdout, stderr = process.communicate()
            print_status(f"Erreur démarrage: {stderr}", False)
            return False
            
    except Exception as e:
        print_status(f"Erreur démarrage backend: {e}", False)
        return False

def test_backend():
    """Teste si le backend répond"""
    print_header("TEST DU BACKEND")
    
    import urllib.request
    import json
    
    test_urls = [
        ("Health Check", "http://localhost:8000/api/health"),
        ("Sessions API", "http://localhost:8000/api/session/sessions"),
        ("API Docs", "http://localhost:8000/docs")
    ]
    
    all_good = True
    for name, url in test_urls:
        try:
            response = urllib.request.urlopen(url, timeout=5)
            if response.status == 200:
                print_status(f"{name}: OK", True)
            else:
                print_status(f"{name}: HTTP {response.status}", False)
                all_good = False
        except Exception as e:
            print_status(f"{name}: Erreur - {e}", False)
            all_good = False
    
    return all_good

def main():
    print("🚀 CORRECTION AUTOMATIQUE BACKEND EAZZYLOTTO")
    print("=" * 60)
    
    # Changer vers le répertoire backend si nécessaire
    if os.path.basename(os.getcwd()) != 'backend':
        if os.path.exists('backend'):
            os.chdir('backend')
            print("📁 Changement vers le dossier backend")
        else:
            print("❌ Dossier backend non trouvé")
            return False
    
    success_count = 0
    total_steps = 5
    
    # Étape 1: Libérer le port 8000
    if kill_process_on_port(8000):
        success_count += 1
    
    # Étape 2: Installer les dépendances
    if install_dependencies():
        success_count += 1
    
    # Étape 3: Corriger main.py
    if fix_main_py():
        success_count += 1
    
    # Étape 4: Démarrer le backend
    if start_backend():
        success_count += 1
        
        # Étape 5: Tester le backend
        time.sleep(2)  # Laisser le temps au serveur de démarrer
        if test_backend():
            success_count += 1
    
    # Résumé final
    print_header("RÉSUMÉ FINAL")
    print(f"Étapes réussies: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("\n🎉 SUCCÈS COMPLET !")
        print("✅ Tous les problèmes ont été résolus")
        print("✅ Backend démarré et fonctionnel")
        print("\n🔗 LIENS UTILES:")
        print("• Backend: http://localhost:8000")
        print("• API Docs: http://localhost:8000/docs")
        print("• Sessions: http://localhost:8000/api/session/sessions")
        print("• Diagnostic Frontend: http://localhost:8081/session-diagnostic.html")
        print("\n💡 Votre plateforme EazzyLotto est maintenant opérationnelle !")
    else:
        print(f"\n⚠️ {total_steps - success_count} problème(s) restant(s)")
        print("Consultez les messages d'erreur ci-dessus pour plus de détails.")
    
    return success_count == total_steps

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
