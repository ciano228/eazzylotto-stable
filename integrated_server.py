#!/usr/bin/env python3
"""
Serveur intégré pour EazzyCalculator avec backend FastAPI
"""
import uvicorn
import webbrowser
import threading
import time
import os
import sys
from pathlib import Path

def start_integrated_server():
    """Démarre le serveur FastAPI intégré"""
    try:
        # Changer vers le dossier backend
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        # Ajouter le dossier backend au path Python
        sys.path.insert(0, str(backend_dir))
        
        print("Démarrage du serveur intégré EazzyCalculator...")
        print("Backend FastAPI + Frontend statique")
        print("Interface: http://localhost:8001/katula-dynamic.html")
        print("API: http://localhost:8001/api")
        print("Appuyez sur Ctrl+C pour arrêter")
        
        # Ouvrir le navigateur après 3 secondes
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8001/katula-dynamic.html")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Démarrer le serveur FastAPI
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\nServeur arrêté")
    except Exception as e:
        print(f"Erreur: {e}")
        print("Assurez-vous que le dossier backend existe et contient main.py")

if __name__ == "__main__":
    start_integrated_server()