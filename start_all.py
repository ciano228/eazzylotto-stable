#!/usr/bin/env python3
"""
Script de démarrage complet pour EazzyCalculator
Lance automatiquement le backend (port 8000) et le frontend (port 8081)
"""
import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

def check_port_available(port):
    """Vérifie si un port est disponible"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

def print_banner():
    """Affiche la bannière de démarrage"""
    print("=" * 60)
    print("   EAZZYCALCULATOR - DÉMARRAGE AUTOMATIQUE")
    print("=" * 60)
    print()

def start_backend():
    """Démarre le backend FastAPI sur le port 8881 (integrated_server.py)"""
    integrated_server_path = Path(__file__).parent / "integrated_server.py"
    
    if not integrated_server_path.exists():
        print("❌ Erreur: Fichier integrated_server.py introuvable")
        return None
    
    print("🚀 Démarrage du backend (integrated_server.py sur port 8881)...")
    
    # Lancer integrated_server.py directement
    process = subprocess.Popen(
        [sys.executable, str(integrated_server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process

def start_frontend():
    """Démarre le serveur HTTP pour le frontend sur le port 8081"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Erreur: Dossier frontend introuvable")
        return None
    
    print("🌐 Démarrage du frontend (port 8081)...")
    
    # Lancer le serveur HTTP simple
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8081"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process

def monitor_process(process, name, color_code):
    """Surveille et affiche les logs d'un processus"""
    try:
        for line in process.stdout:
            print(f"[{color_code}{name}\033[0m] {line.rstrip()}")
    except Exception as e:
        print(f"❌ Erreur monitoring {name}: {e}")

def open_browser_after_delay():
    """Ouvre le navigateur après un délai pour laisser les serveurs démarrer"""
    time.sleep(5)
    url = "http://localhost:8081/ai-center.html"
    print(f"\n🌐 Ouverture du navigateur sur {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Impossible d'ouvrir le navigateur: {e}")

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier les ports
    if not check_port_available(8881):
        print("⚠️  Le port 8881 est déjà utilisé")
        response = input("Voulez-vous continuer quand même ? (o/N): ")
        if response.lower() != 'o':
            sys.exit(1)
    
    if not check_port_available(8081):
        print("⚠️  Le port 8081 est déjà utilisé")
        response = input("Voulez-vous continuer quand même ? (o/N): ")
        if response.lower() != 'o':
            sys.exit(1)
    
    # Démarrer les serveurs
    backend_process = start_backend()
    if not backend_process:
        print("❌ Échec du démarrage du backend")
        sys.exit(1)
    
    time.sleep(5)  # Laisser le backend démarrer (uvicorn peut être lent)
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Échec du démarrage du frontend")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n✅ Serveurs démarrés avec succès !")
    print("\n" + "=" * 60)
    print("   URLS D'ACCÈS")
    print("=" * 60)
    print("\n📊 FRONTEND (Interface utilisateur):")
    print(f"   • AI Center:           http://localhost:8081/ai-center.html")
    print(f"   • Dashboard:           http://localhost:8081/dashboard.html")
    print(f"   • Katula Dynamic:      http://localhost:8081/katula-dynamic.html")
    print(f"   • Smart Input:         http://localhost:8081/smart-input.html")
    print(f"   • Temporal Analysis:   http://localhost:8081/pages/katula/katula-temporal-analysis.html")
    print(f"   • Win Tracker:         http://localhost:8081/win-tracker.html")
    
    print("\n🔧 BACKEND (API):")
    print(f"   • API Base:            http://localhost:8881/api")
    print(f"   • Verdict AI:          http://localhost:8881/api/verdict/analyze")
    print(f"   • Analytics:           http://localhost:8881/api/analytics")
    print(f"   • Performance:         http://localhost:8881/api/performance")
    
    print("\n" + "=" * 60)
    print("   Appuyez sur Ctrl+C pour arrêter tous les serveurs")
    print("=" * 60 + "\n")
    
    # Démarrer les threads de monitoring
    backend_thread = threading.Thread(
        target=monitor_process, 
        args=(backend_process, "BACKEND", "\033[94m"),  # Bleu
        daemon=True
    )
    frontend_thread = threading.Thread(
        target=monitor_process, 
        args=(frontend_process, "FRONTEND", "\033[92m"),  # Vert
        daemon=True
    )
    
    backend_thread.start()
    frontend_thread.start()
    
    # Ouvrir le navigateur après un délai
    browser_thread = threading.Thread(target=open_browser_after_delay, daemon=True)
    browser_thread.start()
    
    try:
        # Attendre indéfiniment (les processus tournent en arrière-plan)
        while True:
            time.sleep(1)
            
            # Vérifier si les processus sont toujours actifs
            if backend_process.poll() is not None:
                print("\n❌ Le backend s'est arrêté de manière inattendue")
                break
            if frontend_process.poll() is not None:
                print("\n❌ Le frontend s'est arrêté de manière inattendue")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt des serveurs en cours...")
        
        # Arrêter proprement les processus
        backend_process.terminate()
        frontend_process.terminate()
        
        # Attendre la fin des processus
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("⚠️  Forçage de l'arrêt des processus...")
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Serveurs arrêtés avec succès")
        print("\nÀ bientôt ! 👋\n")

if __name__ == "__main__":
    main()
