from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(
    title="EazzyCalculator API",
    description="API pour l'analyse et la prédiction des numéros de loterie",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines pour le développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes de base d'abord
@app.get("/")
async def root():
    return {"message": "EazzyCalculator API is running"}

@app.get("/api")
async def api_root():
    return {"message": "EazzyCalculator API is running"}

@app.get("/api/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy", "message": "Backend EazzyLotto opérationnel"}

# Essayer d'importer et monter les routes avec gestion d'erreurs
try:
    from app.database.connection import engine, Base
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée")
except Exception as e:
    print(f"⚠️ Erreur base de données: {e}")

# Importer les routers avec gestion d'erreurs
routers_config = [
    ("app.routes.session", "session_router", "/api/session", ["session"]),
    ("app.routes.analytics", "analytics_router", "", []),  # Analytics sans préfixe
    ("app.routes.lottery", "lottery_router", "/api/lottery", ["lottery"]),
    ("app.routes.analysis", "analysis_router", "/api/analysis", ["analysis"]),
    ("app.routes.katooling_workflow", "katooling_workflow_router", "/api/katooling", ["katooling"])
]

for module_name, router_name, prefix, tags in routers_config:
    try:
        module = __import__(module_name, fromlist=[router_name])
        router = getattr(module, "router")
        
        if prefix:
            app.include_router(router, prefix=prefix, tags=tags)
        else:
            app.include_router(router)
        
        print(f"✅ Router {router_name} monté sur {prefix or '/'}")
    except Exception as e:
        print(f"⚠️ Erreur import {router_name}: {e}")

# Routes de test supplémentaires
@app.get("/api/test")
async def test_endpoint():
    return {"status": "test", "message": "Endpoint de test fonctionnel"}

@app.get("/api/session/test")
async def test_session():
    return {"status": "session_test", "sessions": []}

@app.get("/api/analytics/test")
async def test_analytics():
    return {"status": "analytics_test", "data": {}}

# Servir les fichiers statiques du frontend (à la fin)
try:
    app.mount("/assets", StaticFiles(directory="../frontend/assets"), name="assets")
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
    print("✅ Fichiers statiques montés")
except Exception as e:
    print(f"⚠️ Erreur fichiers statiques: {e}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur EazzyLotto...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
