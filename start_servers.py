#!/usr/bin/env python3
"""
Script pour démarrer le frontend et le backend en même temps
"""
import subprocess
import sys
import time
import os

def start_backend():
    """Démarre le serveur backend"""
    print("🔧 Démarrage du backend...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ]
    return subprocess.Popen(backend_cmd, cwd="backend")

def start_frontend():
    """Démarre le serveur frontend"""
    print("🎨 Démarrage du frontend...")
    frontend_cmd = [sys.executable, "start_frontend.py"]
    return subprocess.Popen(frontend_cmd)

if __name__ == "__main__":
    print("🚀 Démarrage des serveurs...")
    
    # Démarrer le backend
    backend_process = start_backend()
    time.sleep(2)  # Attendre que le backend démarre
    
    # Démarrer le frontend
    frontend_process = start_frontend()
    time.sleep(1)
    
    print("\n✅ Serveurs démarrés !")
    print("🔧 Backend: http://localhost:8000")
    print("🎨 Frontend: http://localhost:8080")
    print("🎯 Interface: http://localhost:8080/katula-dynamic.html")
    print("🔬 Validation KATOOLING: http://localhost:8080/katooling-validation.html")
    print("\n💡 Appuyez sur Ctrl+C pour arrêter les deux serveurs")
    
    try:
        # Attendre que les processus se terminent
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt des serveurs...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Serveurs arrêtés")