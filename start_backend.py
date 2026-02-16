"""
Script de démarrage simplifié pour EazzyCalculator
Lance le serveur backend avec toutes les fonctionnalités
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(backend_dir / ".env")

def main():
    """Point d'entrée principal"""
    
    print("=" * 60)
    print("🚀 DÉMARRAGE EAZZYCALCULATOR")
    print("=" * 60)
    print()
    print("📊 Configuration:")
    print(f"   - Backend: FastAPI")
    print(f"   - Base de données: PostgreSQL")
    print(f"   - Port: 8000")
    print()
    print("🌐 URLs d'accès:")
    print("   - API: http://localhost:8000")
    print("   - Documentation: http://localhost:8000/api/docs")
    print("   - Frontend: http://localhost:8000/")
    print()
    print("=" * 60)
    print()
    
    # Démarrer le serveur
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        app_dir=str(backend_dir)
    )

if __name__ == "__main__":
    main()
