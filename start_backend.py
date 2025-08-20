#!/usr/bin/env python3
"""
Script de démarrage du backend EazzyCalculator sur le port 8081
"""
import uvicorn
import os
import sys
from pathlib import Path

# Ajouter le dossier backend au path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("[BACKEND] Demarrage du serveur backend sur le port 8081...")
    print("[INFO] Endpoints disponibles:")
    print("  - http://localhost:8081/api/health")
    print("  - http://localhost:8081/api/analytics/katula/formes/mundo")
    print("  - http://localhost:8081/api/analytics/katula/table/mundo")
    print("[INFO] Appuyez sur Ctrl+C pour arreter")
    
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8081,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[STOP] Backend arrete")