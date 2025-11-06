"""
Script de démarrage pour l'API EazzyCalculator V2
"""
import uvicorn
import os
from pathlib import Path

def main():
    """Fonction principale pour démarrer l'API"""
    # Assurons-nous que nous sommes dans le bon dossier
    os.chdir(Path(__file__).parent)
    
    # Configurer et démarrer l'API
    uvicorn.run(
        "api_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
