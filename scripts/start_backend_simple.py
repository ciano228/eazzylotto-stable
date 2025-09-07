import uvicorn
import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importer l'app
from main import app

if __name__ == "__main__":
    print("🚀 Démarrage du serveur EazzyCalculator...")
    print("📡 API disponible sur: http://localhost:8001")
    print("🔗 Endpoints:")
    print("   - /api/health")
    print("   - /api/formes/real/{universe}")
    print("   - /api/formes/real/{universe}/chip/{chip_number}")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)