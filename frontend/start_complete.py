#!/usr/bin/env python3
"""
Script de démarrage complet pour EazzyCalculator
"""
import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_dependencies():
    """Vérifie les dépendances nécessaires"""
    print_header("VÉRIFICATION DES DÉPENDANCES")
    
    required_files = [
        "backend/main.py",
        "frontend/index.html",
        "backend/app/database/connection.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Fichiers manquants:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Tous les fichiers requis sont présents")
    return True

def init_database():
    """Initialise la base de données"""
    print_header("INITIALISATION DE LA BASE DE DONNÉES")
    
    try:
        # Exécuter le script d'initialisation
        result = subprocess.run([sys.executable, "init_katula_db.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Base de données initialisée avec succès")
            return True
        else:
            print(f"❌ Erreur initialisation BD: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def start_backend():
    """Démarre le serveur backend"""
    print_header("DÉMARRAGE DU BACKEND")
    
    try:
        os.chdir("backend")
        
        # Vérifier si main.py existe, sinon utiliser main_fixed.py
        if os.path.exists("main_fixed.py") and not os.path.exists("main.py"):
            print("📝 Utilisation de main_fixed.py")
            main_file = "main_fixed.py"
        else:
            main_file = "main.py"
        
        cmd = [sys.executable, "-m", "uvicorn", f"{main_file.replace('.py', '')}:app", 
               "--reload", "--host", "0.0.0.0", "--port", "8000"]
        
        print(f"🚀 Démarrage: {' '.join(cmd)}")
        
        # Démarrer en arrière-plan
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(5)
        
        if process.poll() is None:  # Processus toujours en cours
            print("✅ Backend démarré sur http://localhost:8000")
            os.chdir("..")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erreur backend: {stderr.decode()}")
            os.chdir("..")
            return None
            
    except Exception as e:
        print(f"❌ Erreur démarrage backend: {e}")
        os.chdir("..")
        return None

def start_frontend():
    """Démarre le serveur frontend"""
    print_header("DÉMARRAGE DU FRONTEND")
    
    try:
        os.chdir("frontend")
        
        # Utiliser le serveur Python simple
        cmd = [sys.executable, "-m", "http.server", "8081"]
        
        print(f"🚀 Démarrage: {' '.join(cmd)}")
        
        # Démarrer en arrière-plan
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        if process.poll() is None:  # Processus toujours en cours
            print("✅ Frontend démarré sur http://localhost:8081")
            os.chdir("..")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erreur frontend: {stderr.decode()}")
            os.chdir("..")
            return None
            
    except Exception as e:
        print(f"❌ Erreur démarrage frontend: {e}")
        os.chdir("..")
        return None

def open_browser():
    """Ouvre le navigateur après un délai"""
    time.sleep(8)  # Attendre que les serveurs soient prêts
    try:
        webbrowser.open("http://localhost:8081/index.html")
        print("🌐 Navigateur ouvert sur l'application")
    except Exception as e:
        print(f"⚠️ Impossible d'ouvrir le navigateur: {e}")

def main():
    """Fonction principale"""
    print_header("EAZZYCALCULATOR - DÉMARRAGE COMPLET")
    
    # Vérifications préliminaires
    if not check_dependencies():
        print("\n❌ Dépendances manquantes. Arrêt du démarrage.")
        return False
    
    # Initialisation de la base de données
    if not init_database():
        print("\n⚠️ Problème avec la base de données, mais on continue...")
    
    # Démarrage des serveurs
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Impossible de démarrer le backend")
        return False
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Impossible de démarrer le frontend")
        backend_process.terminate()
        return False
    
    # Affichage des informations
    print_header("APPLICATION DÉMARRÉE AVEC SUCCÈS")
    print("🎯 LIENS PRINCIPAUX:")
    print("   • Application: http://localhost:8081/index.html")
    print("   • Dashboard: http://localhost:8081/dashboard.html")
    print("   • Katula Dynamic: http://localhost:8081/katula-dynamic.html")
    print("   • API Backend: http://localhost:8000")
    print("   • Documentation API: http://localhost:8000/docs")
    
    print("\n📱 PAGES DISPONIBLES:")
    pages = [
        "katula-temporal-analysis.html",
        "katula-multi-universe.html", 
        "katula-forme-layout.html",
        "lstm-neural-network.html",
        "pattern-viewer.html",
        "advanced-journal.html"
    ]
    
    for page in pages:
        print(f"   • {page}: http://localhost:8081/{page}")
    
    # Ouvrir le navigateur en arrière-plan
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n⌨️ Appuyez sur Ctrl+C pour arrêter les serveurs...")
    
    try:
        # Attendre indéfiniment
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt des serveurs...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Serveurs arrêtés")
        return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)