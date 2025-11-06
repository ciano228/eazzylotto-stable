#!/usr/bin/env python3
"""
Script de démarrage simple pour EazzyCalculator
Lance le backend et ouvre le frontend
"""
import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def print_info(message):
    """Afficher un message d'information"""
    print(f"[INFO] {message}")

def print_success(message):
    """Afficher un message de succès"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """Afficher un message d'erreur"""
    print(f"[ERROR] {message}")

def start_backend():
    """Démarrer le serveur backend"""
    print_info("Démarrage du serveur backend...")
    
    try:
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.servers.server_postgres_simple:app",
            "--host", "0.0.0.0", 
            "--port", "8081",
            "--reload"
        ], cwd=Path.cwd())
        
        print_success("Backend démarré sur http://localhost:8081")
        return backend_process
        
    except Exception as e:
        print_error(f"Erreur démarrage backend: {e}")
        return None

def open_frontend():
    """Ouvrir le frontend dans le navigateur"""
    print_info("Ouverture du frontend...")
    
    frontend_path = Path("frontend/katula-dynamic.html")
    
    if not frontend_path.exists():
        print_error(f"Fichier frontend non trouvé: {frontend_path}")
        return False
    
    try:
        # Ouvrir dans le navigateur par défaut
        webbrowser.open(f"file://{frontend_path.absolute()}")
        print_success("Frontend ouvert dans le navigateur")
        return True
        
    except Exception as e:
        print_error(f"Erreur ouverture frontend: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 50)
    print("🚀 DÉMARRAGE EAZZYCALCULATOR")
    print("=" * 50)
    
    # Vérifier le répertoire de travail
    print_info(f"Répertoire: {Path.cwd()}")
    
    # Démarrer le backend
    backend_process = start_backend()
    if not backend_process:
        print_error("Impossible de démarrer le backend")
        return
    
    # Attendre que le backend soit prêt
    print_info("Attente du démarrage du backend...")
    time.sleep(3)
    
    # Ouvrir le frontend
    if not open_frontend():
        print_error("Impossible d'ouvrir le frontend")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("✅ APPLICATION DÉMARRÉE AVEC SUCCÈS!")
    print("=" * 50)
    print("🌐 Backend: http://localhost:8081")
    print("🖥️  Frontend: Ouvert dans le navigateur")
    print("📊 Interface: Katula Dynamic Table")
    print("\n💡 UTILISATION:")
    print("1. Sélectionnez un univers (mundo, fruity, etc.)")
    print("2. Cliquez sur 'Charger Univers'")
    print("3. Explorez la table interactive")
    print("\n⚠️  Pour arrêter: Appuyez sur Ctrl+C")
    print("=" * 50)
    
    try:
        # Attendre que l'utilisateur arrête l'application
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Arrêt de l'application...")
        backend_process.terminate()
        print_success("Application arrêtée")

if __name__ == "__main__":
    main()