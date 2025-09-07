#!/usr/bin/env python
"""
Script de démarrage de l'application EazzyCalculator
"""
import uvicorn
import webbrowser
import os
from pathlib import Path

def main():
    # Configuration
    HOST = "0.0.0.0"
    BACKEND_PORT = 8005
    FRONTEND_PORT = 8080
    
    # Chemins absolus
    BASE_DIR = Path(__file__).parent.parent
    FRONTEND_DIR = BASE_DIR / "frontend"
    
    # Démarrage du backend
    print(f"🚀 Démarrage du backend sur http://localhost:{BACKEND_PORT}")
    
    # Assurez-vous que nous sommes dans le bon répertoire pour le backend
    os.chdir(BASE_DIR)
    
    # Démarrer le serveur avec uvicorn
    uvicorn.run(
        "backend.server_postgres_simple:app",
        host=HOST,
        port=BACKEND_PORT,
        reload=True
    )

if __name__ == "__main__":
    main()
