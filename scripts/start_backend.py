#!/usr/bin/env python3
import uvicorn
import sys
import os

# Utiliser le serveur working_server.py qui fonctionne
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'servers')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    print("[BACKEND] Demarrage serveur backend port 8081...")
    print("[API] http://localhost:8081")
    print("[KATULA] http://localhost:8080/katula-dynamic.html")
    
    try:
        uvicorn.run(
            "working_server:app", 
            host="0.0.0.0", 
            port=8081,
            reload=False
        )
    except KeyboardInterrupt:
        print("\n[STOP] Serveur arrete")